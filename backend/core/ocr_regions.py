"""Shared native text proposals, component anchors and bounded crop recognition."""

import logging
import math
import time

import cv2
import numpy as np

from .matching import center, search_windows
from .value_tokens import parse_value

log = logging.getLogger("circuit_sim.ocr")


def failure(diagnostics, stage, exc):
    log.exception("OCR stage %s failed: %s: %.300s", stage, type(exc).__name__, str(exc))
    diagnostics.setdefault("stages", []).append(
        {
            "stage": stage,
            "status": "failed",
            "error_type": type(exc).__name__,
            "message": str(exc)[:300],
        }
    )


def clean_strokes(image):
    """Remove long straight strokes at their measured angles, preserving small glyphs."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    ink = np.uint8(gray < 180) * 255
    minimum = max(70, min(120, min(gray.shape) * 0.12))
    lines = cv2.HoughLinesP(
        ink, 1, np.pi / 360, threshold=25, minLineLength=int(minimum), maxLineGap=4
    )
    mask = np.zeros_like(gray)
    if lines is not None:
        for a, b, c, d in np.asarray(lines).reshape(-1, 4):
            # Only paint the thin measured stroke, never its bounding rectangle.
            cv2.line(mask, (int(a), int(b)), (int(c), int(d)), 255, 2)
    output = gray.copy()
    output[mask > 0] = 255
    return cv2.cvtColor(output, cv2.COLOR_GRAY2BGR), mask


def anchored_regions(image, components, candidate_regions):
    cleaned, _ = clean_strokes(image)
    proposals = []
    for component in components or []:
        found = []
        for window in search_windows(component, image.shape):
            x, y, x2, y2 = window
            for a, b, c, d in candidate_regions(cleaned[y:y2, x:x2]):
                box = (a + x, b + y, c + x, d + y)
                if box[2] - box[0] < 6 or box[3] - box[1] < 5:
                    continue
                found.append(box)
        unique = []
        for box in sorted(set(found), key=lambda b: math.dist(center(b), center(component.bbox))):
            if any(intersection(box, b) / max(1, min(area(box), area(b))) > 0.7 for b in unique):
                continue
            unique.append(box)
            proposals.append(
                {
                    "text": "",
                    "bbox": list(box),
                    "confidence": 0.5,
                    "component_id": component.id,
                    "context": component.type,
                }
            )
            if len(unique) >= 6:
                break
    return cleaned, proposals


def area(box):
    return (box[2] - box[0]) * (box[3] - box[1])


def intersection(a, b):
    return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))


def quality(item, context=None):
    value = parse_value(item["text"], context or item.get("context"))
    rank = 0 if not value else 1 if value["number"] is None else 3 if value["unit"] else 2
    if value and value.get("unit_inferred"):
        rank = (
            2.4
            if "contextual_unit_lookalike" in value.get("normalizations", [])
            or value.get("has_prefix")
            else 2
        )
    if item.get("unit_hint") == "ohm" and value and value["number"] is not None:
        rank = max(rank, 2.6)
    return rank, item.get("confidence", 0)


def unit_glyph_hint(image, box):
    """An open-bottom, wide, symmetric final glyph supports an OCR omega correction.

    This is only geometric evidence, never an accuracy score. Numeric zero has
    a closed bottom; nine has a narrow/asymmetric descender. Association still
    requires a nearby resistor and caps inferred confidence.
    """
    x, y, x2, y2 = map(int, box)
    crop = image[max(0, y) : max(0, y2), max(0, x) : max(0, x2)]
    if not crop.size:
        return None
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if crop.ndim == 3 else crop
    count, labels, stats, _ = cv2.connectedComponentsWithStats(np.uint8(gray < 160))
    glyphs = sorted(
        (s for s in stats[1:count] if s[cv2.CC_STAT_AREA] >= 4 and s[cv2.CC_STAT_HEIGHT] >= 5),
        key=lambda s: s[0],
    )
    if len(glyphs) < 2:
        return None
    gx, gy, w, h, _ = glyphs[-1]
    if not 0.75 <= w / max(1, h) <= 1.8 or h < max(g[3] for g in glyphs) * 0.7:
        return None
    ink = gray[gy : gy + h, gx : gx + w] < 160
    symmetry = 1 - np.mean(ink != np.fliplr(ink))
    bottom = ink[max(0, h - 2) :]
    mid = bottom[:, max(0, w // 3) : max(1, 2 * w // 3)].mean()
    feet = max(bottom[:, : max(1, w // 3)].mean(), bottom[:, max(1, 2 * w // 3) :].mean())
    if symmetry > 0.62 and mid < 0.25 and feet > 0.25:
        return {"unit": "ohm", "glyphs": len(glyphs)}
    return None


def merge_readings(items):
    kept = []
    for item in sorted(items, key=quality, reverse=True):
        match = next(
            (
                other
                for other in kept
                if intersection(item["bbox"], other["bbox"])
                / max(1, min(area(item["bbox"]), area(other["bbox"])))
                > 0.65
            ),
            None,
        )
        if match:
            match.setdefault("alternatives", []).append(
                {
                    key: item[key]
                    for key in ["text", "bbox", "confidence", "engine", "rotation"]
                    if key in item
                }
            )
        else:
            kept.append(dict(item))
    return sorted(kept, key=lambda item: (item["bbox"][1], item["bbox"][0]))


def crop_variants(image, proposals, reader, deadline, diagnostics, check=lambda: None):
    results = []
    attempts = {}
    component_deadlines = {}
    from .config import load_config

    component_seconds = load_config().get("analysis", {}).get("component_ocr_seconds", 1.5)
    for item in proposals:
        check()
        if time.monotonic() >= deadline:
            diagnostics["budget_exceeded"] = True
            break
        owner = item.get("component_id", "global")
        component_deadlines.setdefault(
            owner,
            min(
                deadline,
                time.monotonic()
                + max(
                    0, component_seconds - diagnostics.get("component_seconds", {}).get(owner, 0)
                ),
            ),
        )
        if attempts.get(owner, 0) >= 2:
            continue
        x, y, x2, y2 = map(int, item["bbox"])
        crop = image[y:y2, x:x2]
        if not crop.size:
            continue
        attempts[owner] = attempts.get(owner, 0) + 1
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        vertical = gray.shape[0] > gray.shape[1] * 1.35
        variants = [(gray, 0)]
        if vertical:
            variants = [
                (cv2.rotate(gray, cv2.ROTATE_90_CLOCKWISE), 90),
                (cv2.rotate(gray, cv2.ROTATE_90_COUNTERCLOCKWISE), -90),
            ]
        # Two contrast variants are fallbacks, not a Cartesian product of retries.
        variants.append(
            (
                cv2.threshold(variants[0][0], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
                variants[0][1],
            )
        )
        variants.append(
            (
                cv2.adaptiveThreshold(
                    variants[0][0],
                    255,
                    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                    cv2.THRESH_BINARY,
                    21,
                    8,
                ),
                variants[0][1],
            )
        )
        for raw, rotation in variants:
            check()
            if time.monotonic() >= component_deadlines[owner]:
                diagnostics["budget_exceeded"] = True
                break
            factor = max(1, 48 / max(1, raw.shape[0] - 8))
            enlarged = cv2.resize(raw, None, fx=factor, fy=factor, interpolation=cv2.INTER_CUBIC)
            h, w = enlarged.shape
            try:
                recognized = reader.recognize(
                    enlarged,
                    horizontal_list=[[0, w, 0, h]],
                    free_list=[],
                    detail=1,
                    paragraph=False,
                    batch_size=1,
                    workers=0,
                )
                for _, text, confidence in recognized:
                    results.append(
                        {
                            **item,
                            "text": text,
                            "confidence": float(confidence),
                            "engine": "easyocr-crop",
                            "rotation": rotation,
                        }
                    )
            except Exception as exc:
                failure(diagnostics, "easyocr-crop", exc)
                break
            if results and quality(results[-1], item.get("context"))[0] == 3:
                break
    return results


def paragraph_text(items):
    """Group word-level boxes before deciding whether a line is problem prose."""
    lines = []
    for item in sorted(items, key=lambda i: (i["bbox"][1], i["bbox"][0])):
        x, y, x2, y2 = item["bbox"]
        cy = (y + y2) / 2
        line = next(
            (line for line in lines if abs(line["cy"] - cy) < max(8, (y2 - y) * 0.65)),
            None,
        )
        if line is None:
            line = {"cy": cy, "items": []}
            lines.append(line)
        line["items"].append(item)
    prose = []
    for line in lines:
        words = sorted(line["items"], key=lambda i: i["bbox"][0])
        text = " ".join(item["text"] for item in words)
        if len(text) > 40 or len(text.split()) > 7:
            prose.append(text)
    return "\n".join(prose)
