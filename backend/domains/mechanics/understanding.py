"""Coarse native figure proposals; these are layout hypotheses, not recognition."""

import cv2
import numpy as np


def understand(image, style):
    h, w = image.shape[:2]
    ratio = min(1.0, 800.0 / max(h, w))
    small = cv2.resize(image, None, fx=ratio, fy=ratio) if ratio < 1 else image
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    ink = np.uint8(gray < min(220.0, float(np.median(gray)) - 25.0)) * 255
    joined = cv2.dilate(ink, np.ones((9, 9), np.uint8))
    contours, _ = cv2.findContours(joined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    regions = []
    for contour in contours:
        x, y, width, height = cv2.boundingRect(contour)
        if width >= 45 * ratio and height >= 45 * ratio and width * height > gray.size * 0.003:
            regions.append(
                [
                    max(0.0, (x - 8) / ratio),
                    max(0.0, (y - 8) / ratio),
                    min(float(w), (x + width + 8) / ratio),
                    min(float(h), (y + height + 8) / ratio),
                ]
            )
    return dict(
        style=style,
        figure_candidates=sorted(regions, key=lambda r: (r[0], r[1]))[:16],
        interpretation="coarse_layout_only",
        coordinate_system="native_image_pixels_x_right_y_down",
    )


def select_region(regions, requested, width, height):
    if requested is None:
        return sorted(regions, key=lambda b: (b[0], b[1]))[0]
    if (
        not isinstance(requested, (list, tuple))
        or len(requested) != 4
        or not all(isinstance(v, (int, float)) and np.isfinite(v) for v in requested)
    ):
        raise ValueError("invalid_figure_region")
    x, y, right, bottom = map(float, requested)
    if not 0 <= x < right <= width or not 0 <= y < bottom <= height:
        raise ValueError("invalid_figure_region")
    return [x, y, right, bottom]
