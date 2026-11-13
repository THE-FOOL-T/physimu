"""Optional Gemini crop reader. No network call without per-request consent."""

import base64
import json
import os
import re
from typing import Protocol
import cv2
import httpx
from .value_tokens import parse_value, normalize, NUM


class LabelReader(Protocol):
    def read_labels(self, crop) -> list[dict]: ...


def valid_label(text):
    text = normalize(text).strip()
    name = r"(?:[RCLVK]\d+|E\d*|ε)"
    unit = r"(?:Ω|Ω|ohms?|volts?|amps?|farad|[VAFHW])"
    pattern = r"(?:(?:" + name + r")\s*=?\s*)?(?:" + NUM + r"\s*[pnuµμmkKMG]?\s*" + unit + r"|\?)?"
    return bool(text and re.fullmatch(pattern, text) and parse_value(text))


class GeminiLabelReader:
    def __init__(self, key, model, client=None):
        if not re.fullmatch(r"[A-Za-z0-9._-]+", model):
            raise ValueError("Invalid model identifier")
        self.key, self.model, self.client = key, model, client

    def read_labels(self, crop):
        ok, encoded = cv2.imencode(".png", crop)
        if not ok:
            return []
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": 'Transcribe only the visible circuit label. Do not infer a missing value. Return JSON {"text":"..."}. Vocabulary: R/C/L/V/E/K with digits, SI values and units, Bangla digits. Empty string if unreadable.'
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": base64.b64encode(encoded).decode(),
                            }
                        },
                    ]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0,
            },
        }
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            + self.model
            + ":generateContent"
        )
        if self.client is not None:
            response = self.client.post(url, headers={"x-goog-api-key": self.key}, json=payload)
        else:
            with httpx.Client(timeout=8) as client:
                response = client.post(url, headers={"x-goog-api-key": self.key}, json=payload)
        response.raise_for_status()
        raw = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        text = json.loads(raw).get("text", "")
        if not isinstance(text, str) or not valid_label(text):
            return []
        return [
            {
                "text": text,
                "bbox": [0, 0, crop.shape[1], crop.shape[0]],
                "confidence": 0.65,
                "source": "vlm",
            }
        ]


def configured_reader():
    key = os.getenv("CIRCUIT_LABEL_API_KEY")
    model = os.getenv("CIRCUIT_LABEL_MODEL")
    return GeminiLabelReader(key, model) if key and model else None


def read_crops(image, reader, items, deadline=float("inf"), check=lambda: None):
    """Enforce crop geometry and vocabulary even for custom provider adapters."""
    from .ocr_tiles import candidate_regions, merge

    candidates = [
        tuple(map(int, item["bbox"]))
        for item in items
        if item.get("confidence", 0) < 0.7 or parse_value(item.get("text", "")) is None
    ]
    if not candidates:
        candidates = candidate_regions(image)
    results = []
    warnings = []
    h, w = image.shape[:2]
    import time
    import logging

    for box in candidates[:8]:
        check()
        if time.monotonic() >= deadline:
            warnings.append(("time_budget", None))
            break
        x, y, x2, y2 = box
        x = max(0, x - 3)
        y = max(0, y - 3)
        x2 = min(w, x2 + 3)
        y2 = min(h, y2 + 3)
        if x2 <= x or y2 <= y or (x2 - x) * (y2 - y) > 0.2 * w * h or y2 - y > 160 or x2 - x > 640:
            continue
        try:
            proposals = reader.read_labels(image[y:y2, x:x2].copy())
            for item in proposals:
                if not valid_label(item.get("text", "")):
                    warnings.append(("label_reader_rejected", None))
                    continue
                results.append(
                    {
                        "text": item["text"],
                        "bbox": [x, y, x2, y2],
                        "confidence": min(0.65, item.get("confidence", 0.5)),
                        "source": "vlm",
                    }
                )
        except Exception as exc:
            logging.getLogger("circuit_sim.pipeline").exception(
                "Label crop failed: %s", type(exc).__name__
            )
            warnings.append(("label_reader_failed", None))
    return merge(results), warnings
