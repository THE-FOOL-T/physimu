"""Bounded skeleton repairs with explicit uncertainty and missing-part evidence."""

import math

import cv2
import numpy as np


def tangent(adj, point, steps=6):
    previous = point
    current = next(iter(adj[point]))
    for _ in range(steps):
        following = adj[current] - {previous}
        if len(following) != 1:
            break
        previous, current = current, next(iter(following))
    delta = np.array(point, float) - current
    return delta / max(1e-9, np.linalg.norm(delta))


def prune_spurs(adj, width, components):
    protected = [t.xy for c in components for t in c.terminals]
    for p in list(adj):
        if p not in adj or len(adj[p]) != 1:
            continue
        if any(math.dist(p, xy) < max(5, width * 3) for xy in protected):
            continue
        path = [p]
        prev = p
        current = next(iter(adj[p]))
        while len(adj[current]) == 2 and len(path) <= max(3, width * 3):
            path.append(current)
            prev, current = current, next(iter(adj[current] - {prev}))
        if len(adj[current]) >= 3 and len(path) <= max(3, width * 3):
            for q in path:
                for neighbor in adj[q]:
                    adj[neighbor].discard(q)
                del adj[q]


def separate_crossings(adj, binary, annotations, width):
    warnings = []
    distance = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
    branches = {p for p in adj if len(adj[p]) >= 3}
    while branches:
        start = min(branches)
        cluster = {start}
        stack = [start]
        branches.remove(start)
        while stack:
            p = stack.pop()
            near = [q for q in branches if math.dist(q, p) <= max(2, width * 2)]
            for q in near:
                branches.remove(q)
                cluster.add(q)
                stack.append(q)
        # Include short degree-two links between adjacent three-way centers.
        region = {p for p in adj if any(math.dist(p, q) <= max(1, width) for q in cluster)}
        ports = {q for p in region for q in adj[p] if q not in region}
        if len(ports) != 4:
            continue  # A T-junction is connected.
        center = np.mean(list(cluster), axis=0)
        x, y = center
        dotted = any(
            a.get("type") == "junction"
            and a["bbox"][0] - 3 <= x <= a["bbox"][2] + 3
            and a["bbox"][1] - 3 <= y <= a["bbox"][3] + 3
            for a in annotations
        )
        peak = max(distance[p[1], p[0]] for p in region)
        if dotted or peak > max(width * 1.35, width / 2 + 1.8):
            continue
        left = set(ports)
        pairs = []
        stable = True
        while left:
            a = min(left)
            left.remove(a)
            va = np.array(a) - center
            b = min(
                left,
                key=lambda q: (
                    np.dot(va, np.array(q) - center)
                    / max(1e-9, np.linalg.norm(np.array(q) - center))
                ),
            )
            vb = np.array(b) - center
            left.remove(b)
            if np.dot(va, vb) / max(1e-9, np.linalg.norm(va) * np.linalg.norm(vb)) > -0.85:
                stable = False
                break
            pairs.append((a, b))
        if not stable:
            continue
        for p in region:
            for q in adj[p]:
                if q not in region:
                    adj[q].discard(p)
        for p in region:
            del adj[p]
        for a, b in pairs:
            adj[a].add(b)
            adj[b].add(a)
        warnings.append(("ambiguous_crossing", f"xy:{round(x)},{round(y)}"))
    return warnings


def repair_gaps(
    adj, components, blocked, width, handwritten=False, repair=True, check=lambda: None
):
    warnings = []
    ghosts = []
    sizes = [
        math.dist(c.terminals[0].xy, c.terminals[1].xy)
        for c in components
        if c.bbox[2] > c.bbox[0] and c.bbox[3] > c.bbox[1]
    ]
    symbol = float(np.median(sizes)) if sizes else 0.0
    limit = (
        min(28, max(12, symbol * 0.45 + width * 2))
        if repair and symbol
        else (12 if handwritten else 6)
    )
    ends = sorted(p for p in adj if len(adj[p]) == 1)
    boxes = [c.bbox for c in components if c.bbox[2] > c.bbox[0] and c.bbox[3] > c.bbox[1]]
    parent = {p: p for p in adj}

    def find(p):
        while parent[p] != p:
            parent[p] = parent[parent[p]]
            p = parent[p]
        return p

    def join(p, q):
        parent[find(p)] = find(q)

    for p, neighbors in adj.items():
        for q in neighbors:
            join(p, q)
    for index, p in enumerate(ends):
        check()
        if len(adj[p]) != 1:
            continue
        direction = tangent(adj, p)
        for q in sorted(ends[index + 1 :], key=lambda q: math.dist(p, q)):
            if len(adj[q]) != 1:
                continue
            if find(p) == find(q):
                continue
            d = math.dist(p, q)
            if d <= 1 or d > max(limit, symbol * 2):
                continue
            delta = (np.array(q) - p) / d
            other = tangent(adj, q)
            if np.dot(direction, delta) < 0.96 or np.dot(other, -delta) < 0.96:
                continue
            samples = [
                np.array(p) + (np.array(q) - p) * f for f in np.linspace(0.05, 0.95, max(3, int(d)))
            ]
            if any(
                any(
                    x + 1 < r[0] < right - 1 and y + 1 < r[1] < bottom - 1
                    for x, y, right, bottom in boxes
                )
                for r in samples
            ):
                continue
            if any(blocked[round(r[1]), round(r[0])] for r in samples):
                continue
            # Never bridge through a different stroke/crossing on the way.
            occupied = set(adj) - {p, q} - adj[p] - adj[q]
            if any((round(r[0]), round(r[1])) in occupied for r in samples[2:-2]):
                continue
            if d > limit:
                ghosts.append(
                    {
                        "bbox": [
                            min(p[0], q[0]) - 6,
                            min(p[1], q[1]) - 6,
                            max(p[0], q[0]) + 6,
                            max(p[1], q[1]) + 6,
                        ],
                        "from": list(p),
                        "to": list(q),
                        "reason": "missing_part",
                    }
                )
                continue
            adj[p].add(q)
            adj[q].add(p)
            join(p, q)
            warnings.append(("gap_bridged", None))
            break
        if not repair or len(adj[p]) != 1:
            continue
        # A bounded first-hit ray can repair a missing T contact. It stops at
        # the first stroke; it cannot jump over a crossing to another endpoint.
        for distance in range(2, round(limit) + 1):
            location = np.array(p) + direction * distance
            x, y = map(round, location)
            if not (0 <= x < blocked.shape[1] and 0 <= y < blocked.shape[0]):
                break
            if blocked[y, x] or any(
                a + 1 < x < c - 1 and b + 1 < y < d - 1 for a, b, c, d in boxes
            ):
                break
            radius = max(1, min(3, round(width)))
            nearby = [
                (x + dx, y + dy)
                for dx in range(-radius, radius + 1)
                for dy in range(-radius, radius + 1)
                if (x + dx, y + dy) in adj and find((x + dx, y + dy)) != find(p)
            ]
            if not nearby:
                continue
            q = min(nearby, key=lambda q: math.dist(q, location))
            adj[p].add(q)
            adj[q].add(p)
            join(p, q)
            warnings.append(("gap_bridged", None))
            break
    return warnings, ghosts
