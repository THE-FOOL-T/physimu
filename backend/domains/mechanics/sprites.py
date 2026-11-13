"""Conservative native body cut-outs and measured static-line repairs."""

import cv2
import numpy as np

from .geometry import foreground


def body_mask(image, bbox, static_lines=()):
    h, w = image.shape[:2]
    x, y, z, v = map(int, bbox)
    x, y, z, v = max(0, x - 3), max(0, y - 3), min(w, z + 4), min(h, v + 4)
    mask = foreground(image[y:v, x:z])
    for a, b in static_lines:
        cv2.line(
            mask,
            tuple(np.rint(np.array(a) - [x, y]).astype(int)),
            tuple(np.rint(np.array(b) - [x, y]).astype(int)),
            0,
            3,
        )
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = [c for c in contours if cv2.contourArea(c) > 0.12 * (z - x) * (v - y)]
    if not candidates:
        return {
            "polygon": [
                [float(bbox[0]), float(bbox[1])],
                [float(bbox[2]), float(bbox[1])],
                [float(bbox[2]), float(bbox[3])],
                [float(bbox[0]), float(bbox[3])],
            ],
            "confidence": 0.0,
            "warning": "mask_unmeasured",
        }
    contour = max(candidates, key=cv2.contourArea)
    polygon = cv2.approxPolyDP(contour, 0.6, True).reshape(-1, 2).astype(float) + [x, y]
    if len(polygon) < 3:
        raise ValueError("mask_unmeasured")
    return {"polygon": polygon.tolist(), "confidence": 0.85, "warning": None}


def repairs(bodies, surfaces):
    result = []
    for surface in surfaces:
        segments = []
        for body in bodies:
            x, y, z, v = body["bbox"]
            rect = (int(x), int(y), max(1, int(z - x) + 1), max(1, int(v - y) + 1))
            for a, b in zip(surface["polyline"], surface["polyline"][1:]):
                hit, p, q = cv2.clipLine(rect, tuple(map(round, a)), tuple(map(round, b)))
                if hit and p != q:
                    segments.append([[float(n) for n in p], [float(n) for n in q]])
        if segments:
            result.append({"surface_or_line_id": surface["id"], "segments": segments})
    return result
