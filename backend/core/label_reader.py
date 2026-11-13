"""Generic opt-in crop transport. Callers own consent, crop limits and vocabulary."""

import base64
import json
import re

import cv2
import httpx


class CropLabelReader:
    def __init__(self, key, model, prompt, *, client=None):
        if not re.fullmatch(r"[A-Za-z0-9._-]+", model):
            raise ValueError("Invalid model identifier")
        self.key, self.model, self.prompt, self.client = key, model, prompt, client

    def read_labels(self, crop, *, timeout=8.0):
        if crop.size == 0 or not 0 < timeout <= 8:
            return []
        ok, encoded = cv2.imencode(".png", crop)
        if not ok:
            return []
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": self.prompt},
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
                "maxOutputTokens": 128,
            },
        }
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        )
        if self.client is None:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(url, headers={"x-goog-api-key": self.key}, json=payload)
        else:
            response = self.client.post(
                url, headers={"x-goog-api-key": self.key}, json=payload, timeout=timeout
            )
        response.raise_for_status()
        raw = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        if not isinstance(raw, str) or len(raw) > 4096:
            return []
        text = json.loads(raw).get("text", "")
        return [{"text": text}] if isinstance(text, str) and len(text) <= 64 else []
