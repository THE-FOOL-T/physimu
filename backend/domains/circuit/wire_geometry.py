"""Ink-based body masks and outward terminal axes, in native pixel space."""

import math

import cv2
import numpy as np


def stroke_width(binary):
    radii = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
    values = radii[radii > 0]
    return max(1.0, float(np.percentile(values, 75)) * 2 - 1) if len(values) else 1.0


def binary_image(image, alternative=False):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image.copy()
    background = cv2.GaussianBlur(gray, (0, 0), max(8, min(gray.shape) / 30))
    normalized = cv2.divide(gray, np.maximum(background, 1), scale=255)
    rough = cv2.threshold(normalized, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    width = stroke_width(rough)
    block = int(np.clip(round(width * 16 + 15), 15, 101)) | 1
    constant = 6 if alternative else 12
    return cv2.adaptiveThreshold(
        normalized,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        block,
        constant,
    )


def ink_at(binary, xy, radius=1):
    x, y = map(lambda v: int(round(v)), xy)
    h, w = binary.shape
    return bool(
        binary[
            max(0, y - radius) : min(h, y + radius + 1),
            max(0, x - radius) : min(w, x + radius + 1),
        ].any()
    )


def refine_terminals(binary, components):
    """Fit a shared lead axis using ink outside both ends, then find body edges.

    An axis change needs support on both sides. Uncertain/missing ink keeps the
    detector axis; refinement never searches an arbitrary neighboring wire.
    """
    width = stroke_width(binary)
    masks = []
    for c in components:
        x, y, right, bottom = c.bbox
        if right <= x or bottom <= y:
            continue
        center = np.array([(x + right) / 2, (y + bottom) / 2])
        original = np.array(c.terminals[1].xy) - np.array(c.terminals[0].xy)
        angle = math.atan2(original[1], original[0]) if np.linalg.norm(original) else 0.0
        candidates = [angle, 0.0, math.pi / 4, math.pi / 2, 3 * math.pi / 4]
        corners = np.array([[x, y], [right, y], [right, bottom], [x, bottom]]) - center
        best = None
        for theta in candidates:
            axis = np.array([math.cos(theta), math.sin(theta)])
            normal = np.array([-axis[1], axis[0]])
            half = float(np.max(np.abs(corners @ axis)))
            for offset in range(
                -min(8, int(min(right - x, bottom - y) * 0.4)),
                min(8, int(min(right - x, bottom - y) * 0.4)) + 1,
            ):
                origin = center + normal * offset
                support = [
                    sum(
                        ink_at(binary, origin + axis * sign * (half + d), radius=0)
                        for d in range(2, 19)
                    )
                    / 17
                    for sign in (-1, 1)
                ]
                quality = min(support) + 0.2 * sum(support) - 0.004 * abs(offset)
                if min(support) >= 0.25 and (best is None or quality > best[0] + 1e-9):
                    best = quality, origin, axis, normal, half
        if best is None:
            axis = original / max(1e-9, np.linalg.norm(original))
            if not np.linalg.norm(axis):
                axis = np.array([1.0, 0.0])
            normal = np.array([-axis[1], axis[0]])
            origin = center
            half = float(np.max(np.abs(corners @ axis)))
        else:
            _, origin, axis, normal, half = best
            if np.dot(axis, original) < 0:
                axis = -axis
                normal = -normal
        across = float(np.max(np.abs((corners + center - origin) @ normal))) + 2
        profile = []
        for distance in np.arange(-half, half + 1):
            occupied = [
                v
                for v in np.arange(-across, across + 1)
                if ink_at(binary, origin + axis * distance + normal * v, radius=0)
            ]
            if occupied and max(occupied) - min(occupied) > max(3, width * 2.2):
                profile.append(distance)
        # No recognizable body: retain the detector's full cut, never join its ends.
        lo, hi = (min(profile) - 1, max(profile) + 1) if len(profile) >= 2 else (-half, half)
        lo, hi = max(-half, lo), min(half, hi)
        for t, distance in zip(c.terminals, (lo, hi)):
            t.xy = tuple(float(v) for v in origin + axis * distance)
        c.orientation_deg = math.degrees(math.atan2(axis[1], axis[0])) % 180
        polygon = np.array(
            [
                origin + axis * d + normal * n
                for d, n in [
                    (lo, -across - 1),
                    (hi, -across - 1),
                    (hi, across + 1),
                    (lo, across + 1),
                ]
            ]
        )
        masks.append(polygon.round().astype(np.int32))
    return masks


def erase_label_preserving_wires(binary, bbox, width):
    """Erase tight glyph ink while retaining a straight continuation on both sides."""
    h, w = binary.shape
    x, y, right, bottom = map(int, bbox)
    x, y, right, bottom = max(0, x), max(0, y), min(w - 1, right), min(h - 1, bottom)
    if right <= x or bottom <= y:
        return
    margin = max(12, int(width * 5))
    a, b, c, d = (
        max(0, x - margin),
        max(0, y - margin),
        min(w, right + margin + 1),
        min(h, bottom + margin + 1),
    )
    crop = binary[b:d, a:c].copy()
    lines = cv2.HoughLinesP(
        crop,
        1,
        np.pi / 360,
        threshold=max(10, margin),
        minLineLength=max(12, min(right - x, bottom - y) + margin),
        maxLineGap=3,
    )
    retained = np.zeros_like(crop)
    if lines is not None:
        for xx, yy, xx2, yy2 in lines.reshape(-1, 4):
            p = np.array([xx + a, yy + b], float)
            q = np.array([xx2 + a, yy2 + b], float)
            delta = q - p
            length = np.linalg.norm(delta)
            if length < 1:
                continue
            unit = delta / length
            # Intersect the measured line with the erased rectangle. Ink must
            # continue outside *both* ends, not merely touch one glyph edge.
            samples = [p + unit * v for v in np.arange(0, length + 1)]
            inside = [
                i for i, r in enumerate(samples) if x <= r[0] <= right and y <= r[1] <= bottom
            ]
            if not inside or min(inside) < 4 or max(inside) > len(samples) - 5:
                continue
            left = samples[max(0, min(inside) - 6) : min(inside)]
            after = samples[max(inside) + 1 : max(inside) + 7]
            if (
                min(sum(ink_at(binary, r) for r in side) / len(side) for side in (left, after))
                < 0.8
            ):
                continue
            cv2.line(retained, (xx, yy), (xx2, yy2), 255, max(1, round(width) + 1))
    # The foreground test shrinks a padded OCR rectangle to its actual glyph ink.
    target = binary[y : bottom + 1, x : right + 1]
    target[target > 0] = 0
    restored = cv2.bitwise_and(crop, retained)
    target[:] = restored[y - b : bottom - b + 1, x - a : right - a + 1]


def terminal_hit(terminal, other, candidates, tolerance, width):
    if not len(candidates):
        return None
    origin = np.array(terminal.xy)
    axis = origin - np.array(other.xy)
    axis /= max(1e-9, np.linalg.norm(axis))
    delta = candidates - origin
    along = delta @ axis
    normal = np.abs(delta[:, 0] * axis[1] - delta[:, 1] * axis[0])
    distance = np.linalg.norm(delta, axis=1)
    allowed = (
        (along >= -max(2, width))
        & (along <= tolerance)
        & (normal <= max(2.5, width * 1.5) + np.maximum(0, along) * 0.08)
    )
    indices = np.flatnonzero(allowed)
    if not len(indices):
        return None
    selected = min(indices, key=lambda i: (max(0, along[i]) + normal[i] * 3, distance[i]))
    return tuple(map(int, candidates[selected])), float(normal[selected])
