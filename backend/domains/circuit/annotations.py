"""Exclude periodic dashed/dotted annotation strokes without erasing crossing wires."""

import math
import cv2
import numpy as np


def dashed_mask(binary):
    mask = np.zeros_like(binary)
    lines = cv2.HoughLinesP(binary, 1, np.pi / 180, threshold=18, minLineLength=55, maxLineGap=18)
    if lines is None:
        return mask
    h, w = binary.shape
    for entry in np.asarray(lines).reshape(-1, 4):
        x, y, x2, y2 = map(int, entry)
        length = math.hypot(x2 - x, y2 - y)
        if length < 55:
            continue
        ux, uy = (x2 - x) / length, (y2 - y) / length
        coords = [(round(x + ux * i), round(y + uy * i)) for i in range(round(length) + 1)]
        ink = [bool(binary[min(h - 1, max(0, b)), min(w - 1, max(0, a))]) for a, b in coords]
        runs = []
        last = ink[0]
        count = 0
        for value in ink:
            if value == last:
                count += 1
            else:
                runs.append((last, count))
                last = value
                count = 1
        runs.append((last, count))
        strokes = [n for value, n in runs if value]
        gaps = [n for value, n in runs if not value]
        if len(strokes) < 4 or len(gaps) < 3:
            continue
        if not (0.18 < np.mean(ink) < 0.88 and max(strokes) <= 24 and 1.5 <= np.median(gaps) <= 18):
            continue
        if np.std(gaps) / max(1, np.mean(gaps)) > 0.65:
            continue
        nx, ny = -uy, ux
        for a, b in coords:
            if not (0 <= a < w and 0 <= b < h):
                continue
            # Continuous ink on both perpendicular sides is a real crossing wire.
            crossing = all(
                0 <= round(a + nx * d) < w
                and 0 <= round(b + ny * d) < h
                and binary[round(b + ny * d), round(a + nx * d)]
                for d in [-7, -5, 5, 7]
            )
            if not crossing:
                cv2.circle(mask, (a, b), 2, 255, -1)
    # A neighboring removal disk must not nick an uninterrupted crossing wire.
    protected = cv2.bitwise_or(
        cv2.morphologyEx(binary, cv2.MORPH_OPEN, np.ones((30, 1), np.uint8)),
        cv2.morphologyEx(binary, cv2.MORPH_OPEN, np.ones((1, 30), np.uint8)),
    )
    mask[protected > 0] = 0
    return mask
