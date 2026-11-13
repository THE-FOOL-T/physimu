"""Conservative, untrained image-statistics style estimate and notebook cleanup."""

import cv2
import numpy as np


def estimate_style(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ratio = min(1, 640 / max(gray.shape))
    gray = cv2.resize(gray, None, fx=ratio, fy=ratio)
    background = cv2.GaussianBlur(gray, (0, 0), 15)
    texture = float(np.std(background))
    ink = (gray < 140).astype(np.uint8) * 255
    distances = cv2.distanceTransform(ink, cv2.DIST_L2, 3)
    widths = distances[distances > 0]
    variance = float(np.std(widths) / max(0.01, np.mean(widths))) if widths.size else 0
    lines = cv2.HoughLinesP(ink, 1, np.pi / 180, threshold=20, minLineLength=30, maxLineGap=3)
    straight = np.zeros_like(ink)
    for line in np.asarray(lines).reshape(-1, 4) if lines is not None else []:
        cv2.line(straight, tuple(line[:2]), tuple(line[2:]), 255, 3)
    straightness = float(
        np.count_nonzero((ink > 0) & (straight > 0)) / max(1, np.count_nonzero(ink))
    )
    photo = texture > 20 and float(np.mean(gray < 220)) > 0.2
    style = (
        "photo" if photo else "handwritten" if straightness < 0.4 and variance > 0.38 else "printed"
    )
    return {
        "style": style,
        "confidence": 0.55,
        "method": "untrained_image_statistics",
        "features": {
            "stroke_width_cv": variance,
            "line_straightness": straightness,
            "background_texture": texture,
        },
    }


def remove_ruling(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mask = np.zeros_like(gray, dtype=bool)
    light = (gray > 110) & (gray < 240)
    for axis in [0, 1]:
        projection = light.mean(axis=axis)
        indices = np.flatnonzero(projection > 0.7)
        groups = np.split(indices, np.flatnonzero(np.diff(indices) > 1) + 1) if len(indices) else []
        groups = [group for group in groups if 0 < len(group) <= 3]
        centers = np.array([np.mean(group) for group in groups])
        gaps = np.diff(centers)
        if len(groups) < 3 or np.median(gaps) < 8 or np.std(gaps) / max(1, np.mean(gaps)) > 0.2:
            continue
        for group in groups:
            if axis == 1:
                mask[group, :] = True
            else:
                mask[:, group] = True
    result = image.copy()
    removable = mask & light
    result[removable] = 255
    return result, bool(np.any(removable))
