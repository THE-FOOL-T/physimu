"""Limited, measured classical recognition for clear single-pendulum diagrams.

These are geometric proposals, never YOLO predictions. No caption, OCR value,
filename or authored scene determines the topology. Ambiguous physical bobs are
retained as candidates instead of being merged by proximity.
"""

import math

import cv2
import numpy as np

from .detect import Detection
from .geometry import foreground


def annotate_alternatives(scene, report):
    """Retain measured depictions as evidence belonging to the same physical link."""
    if not scene["links"]:
        return
    scale = report["native_scale"]
    proposal = report["selected"]
    for i, ghost in enumerate(proposal["alternatives"]):
        center = [float(v * scale) for v in ghost["center"]]
        pivot = [float(v * scale) for v in proposal["pivot"]]
        radius = ghost["radius"] * scale
        scene["annotations"].append(
            dict(
                id=f"alternate_state_{scene['links'][0]['id']}_{i + 1}",
                type="axis",
                geometry=dict(
                    points=[pivot, center],
                    bbox=[
                        center[0] - radius,
                        center[1] - radius,
                        center[0] + radius,
                        center[1] + radius,
                    ],
                ),
            )
        )


def circle_support(ink, center, radius):
    angles = np.linspace(0, 2 * math.pi, 96, endpoint=False)
    values = []
    for r in np.linspace(max(1, radius - 2.5), radius + 2.5, 7):
        x = np.clip(np.rint(center[0] + r * np.cos(angles)).astype(int), 0, ink.shape[1] - 1)
        y = np.clip(np.rint(center[1] + r * np.sin(angles)).astype(int), 0, ink.shape[0] - 1)
        values.append(ink[y, x] > 0)
    return float(np.any(values, axis=0).mean())


def route_support(ink, start, end, radius):
    start, end = np.array(start), np.array(end)
    vector = end - start
    length = float(np.linalg.norm(vector))
    if length < radius * 4:
        return None
    direction = vector / length
    normal = np.array([-direction[1], direction[0]])
    positions = np.linspace(5, length - radius - 3, max(24, round(length)))
    samples = []
    for offset in np.linspace(-2.5, 2.5, 7):
        points = start + positions[:, None] * direction + offset * normal
        x = np.clip(np.rint(points[:, 0]).astype(int), 0, ink.shape[1] - 1)
        y = np.clip(np.rint(points[:, 1]).astype(int), 0, ink.shape[0] - 1)
        samples.append(ink[y, x] > 0)
    occupied = np.any(samples, axis=0)
    changes = np.flatnonzero(np.diff(np.r_[True, occupied, True]))
    gaps = changes[1::2] - changes[::2]
    coverage = float(occupied.mean())
    longest_gap = float(max(gaps, default=0) / len(occupied))
    if coverage < 0.35 or longest_gap > 0.15:
        return None
    return dict(
        coverage=coverage,
        longest_gap_fraction=longest_gap,
        stroke="solid" if coverage > 0.9 else "dashed",
        length_px=length,
    )


def pendulum_proposals(image, check=lambda: None, *, candidate=None):
    """Require support/pivot, a reached round bob and an observed radial trace."""
    h, w = image.shape[:2]
    ratio = min(1.0, 1200 / max(h, w))
    source = cv2.resize(image, None, fx=ratio, fy=ratio) if ratio < 1 else image
    gray = cv2.cvtColor(source, cv2.COLOR_BGR2GRAY)
    ink = foreground(source)
    sh, sw = ink.shape
    circles = []
    contours, _ = cv2.findContours(ink, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        x, y, width, height = cv2.boundingRect(contour)
        area, perimeter = cv2.contourArea(contour), cv2.arcLength(contour, True)
        if (
            min(width, height) >= max(10, min(sh, sw) * 0.012)
            and max(width, height) < min(sh, sw) * 0.16
            and 0.75 < width / height < 1.3
            and area > 0
            and 4 * math.pi * area / max(1, perimeter**2) > 0.72
        ):
            (cx, cy), radius = cv2.minEnclosingCircle(contour)
            circles.append([cx, cy, radius])
    found = cv2.HoughCircles(
        cv2.GaussianBlur(gray, (5, 5), 1),
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=max(12, sh * 0.025),
        param1=100,
        param2=18,
        minRadius=max(6, round(min(sh, sw) * 0.012)),
        maxRadius=round(min(sh, sw) * 0.09),
    )
    for circle in [] if found is None else found[0]:
        if not any(math.dist(circle[:2], c[:2]) < max(6, c[2] * 0.5) for c in circles):
            circles.append(list(map(float, circle)))
    candidates = []
    for cx, cy, radius in circles:
        check()
        coverage = circle_support(ink, (cx, cy), radius)
        if coverage < 0.42:
            continue
        yy, xx = np.ogrid[:sh, :sw]
        interior = gray[(xx - cx) ** 2 + (yy - cy) ** 2 < (radius * 0.65) ** 2]
        fill = float(np.mean(interior < min(235, float(np.median(gray)) - 12)))
        candidates.append(
            dict(
                center=[cx, cy],
                radius=radius,
                outline_coverage=coverage,
                fill=fill,
                score=coverage * 0.55 + fill * 0.45,
            )
        )
    lines = cv2.HoughLinesP(
        ink,
        1,
        np.pi / 720,
        max(25, round(sw * 0.035)),
        minLineLength=max(30, round(min(sh, sw) * 0.16)),
        maxLineGap=max(10, round(sh * 0.025)),
    )
    lines = [] if lines is None else lines[:, 0].tolist()
    horizontal = [
        line
        for line in lines
        if abs(line[3] - line[1]) < 0.035 * abs(line[2] - line[0])
        and abs(line[2] - line[0]) > sw * 0.18
    ]
    proposals = []
    for ceiling in horizontal:
        check()
        y = (ceiling[1] + ceiling[3]) / 2
        left, right = sorted([ceiling[0], ceiling[2]])
        support_trace = route_support(ink, [left, y], [right, y], 0)
        if (
            not support_trace
            or support_trace["coverage"] < 0.9
            or support_trace["longest_gap_fraction"] > 0.035
        ):
            continue
        pivots = []
        for x1, y1, x2, y2 in lines:
            if abs(y2 - y1) < sh * 0.14 or min(y1, y2) > y + sh * 0.09:
                continue
            x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if left - 3 <= x <= right + 3 and y < max(y1, y2):
                group = next((g for g in pivots if abs(np.mean(g) - x) < max(5, sw * 0.012)), None)
                if group is None:
                    pivots.append([x])
                else:
                    group.append(x)
        for group in pivots:
            pivot = [float(np.median(group)), float(y)]
            supported = []
            for circle in candidates:
                if circle["center"][1] < y + circle["radius"] * 4:
                    continue
                route = route_support(ink, pivot, circle["center"], circle["radius"])
                if route:
                    supported.append({**circle, "route": route})
            if not supported:
                continue
            supported.sort(key=lambda c: c["score"], reverse=True)
            best = supported[0]
            # Similar solid circles cannot be silently treated as the same body.
            ambiguous = len(supported) > 1 and best["score"] - supported[1]["score"] < 0.12
            if best["outline_coverage"] < 0.75:
                continue
            ghosts = [
                c
                for c in supported[1:]
                if abs(c["route"]["length_px"] / best["route"]["length_px"] - 1) < 0.1
                and abs(c["radius"] / best["radius"] - 1) < 0.35
            ]
            proposals.append(
                dict(
                    pivot=pivot,
                    support=[left, y, right, y],
                    bob=best,
                    alternatives=ghosts,
                    ambiguous=ambiguous,
                    confidence=min(0.92, best["score"] * 0.7 + best["route"]["coverage"] * 0.3),
                )
            )
            if ambiguous:
                for other in supported[1:]:
                    if best["score"] - other["score"] < 0.12:
                        proposals.append(
                            dict(
                                pivot=pivot,
                                support=[left, y, right, y],
                                bob=other,
                                alternatives=[c for c in supported if c is not other],
                                ambiguous=True,
                                confidence=min(
                                    0.92, other["score"] * 0.7 + other["route"]["coverage"] * 0.3
                                ),
                            )
                        )
    proposals.sort(key=lambda p: p["confidence"], reverse=True)
    unique = []
    for proposal in proposals:
        if not any(
            math.dist(p["pivot"], proposal["pivot"]) < 10
            and math.dist(p["bob"]["center"], proposal["bob"]["center"]) < 10
            for p in unique
        ):
            unique.append(proposal)
    report = dict(
        method="classical_vision",
        supported_family="single_pendulum",
        candidates=unique,
        accepted=False,
        reason="insufficient_geometric_evidence",
        native_scale=1 / ratio,
    )
    if not unique:
        return [], report
    if candidate is not None and (
        not isinstance(candidate, int) or not 0 <= candidate < len(unique)
    ):
        report["reason"] = "invalid_pendulum_candidate"
        return [], report
    selected = unique[candidate if candidate is not None else 0]
    if candidate is None and (
        selected["ambiguous"]
        or (len(unique) > 1 and unique[0]["confidence"] - unique[1]["confidence"] < 0.1)
    ):
        report["reason"] = "ambiguous_pendulum_candidates"
        return [], report

    # Return native coordinates. The normal measure/associate/compiler still runs.
    def native(point):
        return [float(v / ratio) for v in point]

    pivot = native(selected["pivot"])
    center = native(selected["bob"]["center"])
    radius = selected["bob"]["radius"] / ratio
    confidence = selected["confidence"]
    end = np.array(center) - (np.array(center) - pivot) / math.dist(center, pivot) * (radius + 2)
    rope = [
        min(pivot[0], end[0]) - 3,
        min(pivot[1], end[1]) - 2,
        max(pivot[0], end[0]) + 3,
        max(pivot[1], end[1]) + 2,
    ]
    support = native(selected["support"])
    detections = [
        Detection(
            "CV1", "ceiling", [support[0], support[1] - 3, support[2], support[3] + 3], confidence
        ),
        Detection(
            "CV2", "pivot", [pivot[0] - 3, pivot[1] - 3, pivot[0] + 3, pivot[1] + 3], confidence
        ),
        Detection(
            "CV3",
            "bob",
            [center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius],
            confidence,
        ),
        Detection("CV4", "rope", rope, confidence),
    ]
    report.update(
        accepted=True,
        reason="support_pivot_radial_trace_and_unique_bob",
        selected=selected,
        native_scale=1 / ratio,
        confirmed_by_user=candidate is not None,
    )
    return detections, report
