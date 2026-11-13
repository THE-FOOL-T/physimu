"""Native-pixel measurements with explicit fit evidence; no detector-box angles."""

from collections import deque
import math

import cv2
import numpy as np
from scipy.signal import find_peaks

FIT_THRESHOLDS = {
    "printed": dict(line_band=3.5, line_gap=12, circle_band=2.5),
    "handwritten": dict(line_band=7.0, line_gap=20, circle_band=4.5),
}


def thresholds(style):
    return FIT_THRESHOLDS["handwritten" if style == "handwritten" else "printed"]


def foreground(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    border = np.concatenate([gray[0], gray[-1], gray[:, 0], gray[:, -1]])
    return np.uint8(gray < min(220, float(np.median(border)) - 30)) * 255


def crop_mask(image, bbox, exclude=(), pad=3):
    h, w = image.shape[:2]
    x, y, z, v = bbox
    x, y, z, v = (
        max(0, int(x) - pad),
        max(0, int(y) - pad),
        min(w, math.ceil(z) + pad),
        min(h, math.ceil(v) + pad),
    )
    mask = foreground(image[y:v, x:z])
    for a, b, c, d in exclude:
        cv2.rectangle(
            mask, (max(0, int(a) - x), max(0, int(b) - y)), (int(c) - x, int(d) - y), 0, -1
        )
    return mask, np.array([x, y], float)


def fit_line(image, bbox, exclude=(), orientation=None, *, style="printed"):
    settings = thresholds(style)
    mask, offset = crop_mask(image, bbox, exclude)
    lines = cv2.HoughLinesP(
        mask, 1, np.pi / 720, 12, minLineLength=12, maxLineGap=settings["line_gap"]
    )
    if lines is None:
        raise ValueError("line_unmeasured")
    candidates = list(lines[:, 0])
    if orientation:

        def allowed(line):
            dx, dy = abs(line[2] - line[0]), abs(line[3] - line[1])
            if orientation in {"floor", "ceiling"}:
                return dx > 3 * dy
            if orientation == "wall":
                return dy > 3 * dx
            return dx > 0 and 0.08 < dy / dx < 10

        candidates = [line for line in candidates if allowed(line)]
    if not candidates:
        raise ValueError("line_unmeasured")
    points = np.column_stack(np.where(mask > 0)[::-1]).astype(float)

    def support(line):
        a, b, c, d = line
        delta = points - [a, b]
        length = math.hypot(c - a, d - b)
        residual = np.abs((c - a) * delta[:, 1] - (d - b) * delta[:, 0]) / max(1, length)
        return int(np.count_nonzero(residual <= settings["line_band"])), length

    # An occluded incline can have two short collinear pieces, while its rope
    # is one longer piece. Rank all collinear ink, not one Hough span.
    a, b, c, d = max(candidates, key=support)
    direction = np.array([c - a, d - b], float)
    direction /= np.linalg.norm(direction)
    delta = points - np.array([a, b])
    residual = np.abs(direction[0] * delta[:, 1] - direction[1] * delta[:, 0])
    inliers = points[residual <= settings["line_band"]]
    if len(inliers) < 8:
        raise ValueError("line_unmeasured")
    vx, vy, x, y = cv2.fitLine(inliers.astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
    u = np.array([vx, vy], float)
    if u[0] < 0 or abs(u[0]) < 0.001 and u[1] < 0:
        u *= -1
    origin = np.array([x, y])
    t = (inliers - origin) @ u
    endpoints = [origin + u * t.min() + offset, origin + u * t.max() + offset]
    delta = inliers - origin
    error = float(np.median(np.abs(u[0] * delta[:, 1] - u[1] * delta[:, 0])))
    return {
        "points": [p.tolist() for p in endpoints],
        "angle_deg": math.degrees(math.atan2(-u[1], u[0])),
        "length_px": float(t.max() - t.min()),
        "residual_px": error,
        "confidence": min(0.95, 0.95 / (1 + error / 3)),
    }


def fit_circle(image, bbox, *, style="printed"):
    mask, offset = crop_mask(image, bbox, pad=2)
    points = np.column_stack(np.where(mask > 0)[::-1]).astype(float) + offset
    centre = np.array([(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2])
    radius = min(bbox[2] - bbox[0], bbox[3] - bbox[1]) / 2
    distances = np.linalg.norm(points - centre, axis=1)
    lower, upper = (0.5, 1.4) if style == "handwritten" else (0.65, 1.22)
    points = points[(distances > radius * lower) & (distances < radius * upper)]
    if len(points) < 12:
        raise ValueError("circle_unmeasured")
    for _ in range(4):
        A = np.column_stack([2 * points, np.ones(len(points))])
        cx, cy, c = np.linalg.lstsq(A, np.sum(points**2, axis=1), rcond=None)[0]
        radius2 = c + cx * cx + cy * cy
        if radius2 <= 0:
            raise ValueError("circle_unmeasured")
        centre, radius = np.array([cx, cy]), math.sqrt(radius2)
        residual = np.abs(np.linalg.norm(points - centre, axis=1) - radius)
        keep = residual <= max(thresholds(style)["circle_band"], float(np.median(residual)) * 2)
        if keep.all() or keep.sum() < 12:
            break
        points = points[keep]
    if (
        not min(bbox[2] - bbox[0], bbox[3] - bbox[1]) * 0.25
        <= radius
        <= max(bbox[2] - bbox[0], bbox[3] - bbox[1]) * 0.7
    ):
        raise ValueError("circle_unmeasured")
    return {
        "center": centre.tolist(),
        "radius_px": radius,
        "residual_px": float(np.median(residual)),
        "confidence": min(0.95, 0.95 / (1 + float(np.median(residual)) / 3)),
    }


def skeleton(mask):
    mask = mask.copy()
    result = np.zeros_like(mask)
    cross = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    while np.any(mask):
        eroded = cv2.erode(mask, cross)
        result |= cv2.subtract(mask, cv2.dilate(eroded, cross))
        mask = eroded
    return result


def trace(image, bbox, exclude=(), *, style="printed"):
    mask, offset = crop_mask(image, bbox, exclude, pad=4)
    if style == "handwritten":
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    skel = skeleton(mask)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(skel, 8)
    segments = []
    all_points = []
    for label in range(1, count):
        if stats[label, cv2.CC_STAT_AREA] < 8:
            continue
        points = set(zip(*np.where(labels == label)))

        def farthest(start):
            todo = deque([start])
            parent = {start: None}
            end = start
            while todo:
                end = todo.popleft()
                for dy, dx in (
                    (-1, -1),
                    (-1, 0),
                    (-1, 1),
                    (0, -1),
                    (0, 1),
                    (1, -1),
                    (1, 0),
                    (1, 1),
                ):
                    near = (end[0] + dy, end[1] + dx)
                    if near in points and near not in parent:
                        parent[near] = end
                        todo.append(near)
            return end, parent

        a, _ = farthest(min(points))
        b, parent = farthest(a)
        route = []
        p = b
        while p is not None:
            route.append([float(p[1] + offset[0]), float(p[0] + offset[1])])
            p = parent[p]
        if len(route) >= 8:
            segments.append(route[::-1])
            all_points.extend(route)
    if not segments:
        raise ValueError("trace_unmeasured")
    return {"segments": segments, "points": all_points, "confidence": 0.8}


def spring(image, bbox, exclude=(), *, style="printed"):
    measured = trace(image, bbox, exclude, style=style)
    pts = np.array(measured["points"])
    vertical = (bbox[3] - bbox[1]) > (bbox[2] - bbox[0])
    axis = 1 if vertical else 0
    transverse = 1 - axis
    lo, hi = np.min(pts[:, axis]), np.max(pts[:, axis])
    span = max(1, hi - lo)
    start = pts[pts[:, axis] <= lo + max(3, span * 0.04)].mean(axis=0)
    end = pts[pts[:, axis] >= hi - max(3, span * 0.04)].mean(axis=0)
    samples = []
    for k in range(math.floor(lo), math.ceil(hi) + 1):
        selected = pts[np.abs(pts[:, axis] - k) < 0.6, transverse]
        samples.append(float(np.mean(selected)) if len(selected) else np.nan)
    samples = np.array(samples)
    valid = np.isfinite(samples)
    samples = np.interp(np.arange(len(samples)), np.flatnonzero(valid), samples[valid])
    if style == "handwritten":
        samples = cv2.GaussianBlur(samples.astype(np.float32)[None, :], (5, 1), 0.7)[0]
    peaks, _ = find_peaks(samples, prominence=max(2, float(np.ptp(samples)) * 0.35), distance=3)
    return {
        **measured,
        "endpoints": [start.tolist(), end.tolist()],
        "coils": max(1, len(peaks)),
        "vertical": vertical,
    }


def trajectory_arc(image, bbox, origin=None, exclude=()):
    mask, offset = crop_mask(image, bbox, exclude)
    pts = np.column_stack(np.where(skeleton(mask) > 0)[::-1]).astype(float) + offset
    if len(pts) < 12 or np.ptp(pts[:, 0]) < 15:
        raise ValueError("trajectory_unmeasured")
    a, b, c = np.polyfit(pts[:, 0], pts[:, 1], 2)
    error = np.abs(pts[:, 1] - np.polyval([a, b, c], pts[:, 0]))
    keep = error < max(3, float(np.median(error)) * 2)
    a, b, c = np.polyfit(pts[keep, 0], pts[keep, 1], 2)
    x = float(origin[0]) if origin else float(pts[:, 0].min())
    xs = np.linspace(pts[:, 0].min(), pts[:, 0].max(), 40)
    return {
        "coefficients": [float(a), float(b), float(c)],
        "points": [[float(x), float(a * x * x + b * x + c)] for x in xs],
        "angle_deg": math.degrees(math.atan(-(2 * a * x + b))),
        "residual_px": float(np.median(error)),
        "confidence": 0.8,
    }


def pendulum(pivot, bob):
    dx, dy = np.array(bob) - np.array(pivot)
    return {"length_px": math.hypot(dx, dy), "angle_deg": math.degrees(math.atan2(dx, dy))}


def measure_style(image):
    mask = foreground(image)
    border = np.concatenate([image[0], image[-1], image[:, 0], image[:, -1]])
    paper = np.median(border, axis=0)
    pixels = image[mask > 0]
    ink = np.median(pixels, axis=0) if len(pixels) else np.array([32, 32, 32])
    distance = cv2.distanceTransform(mask, cv2.DIST_L2, 3)
    radii = distance[(distance > 0) & (distance < 8)]

    def colour(v):
        return "#" + "".join(f"{int(n):02x}" for n in v[::-1])

    return {
        "paper_color": colour(paper),
        "ink_color": colour(ink),
        "stroke_px": max(1.0, float(np.median(radii)) * 2 if len(radii) else 2.0),
    }
