"""Skeleton extraction, bounded repairs and direction-aware terminal attachment."""

import math

import cv2
import numpy as np
from skimage.morphology import skeletonize

from .netlist import Node, Point, Segment, WireGraph
from .wire_geometry import (
    binary_image,
    stroke_width,
    refine_terminals,
    erase_label_preserving_wires,
    terminal_hit,
)
from .wire_repair import prune_spurs, separate_crossings, repair_gaps


def prepare_trace(
    image,
    components,
    texts=(),
    annotations=(),
    handwritten=False,
    alternative=False,
    repair=True,
    check=lambda: None,
):
    check()
    binary = binary_image(image, alternative)
    h, w = binary.shape
    width = stroke_width(binary)
    from .annotations import dashed_mask

    annotation_mask = dashed_mask(binary)
    binary[annotation_mask > 0] = 0
    if handwritten:
        binary = (cv2.GaussianBlur(binary, (3, 3), 0.5) > 80).astype(np.uint8) * 255
    for item in [*texts, *annotations]:
        check()
        if item.get("type") == "junction":
            continue
        if "text" in item:
            if item.get("wire_overlap") and item.get("outcome") != "assigned":
                continue
            from .values import parse_value

            parsed = parse_value(item["text"])
            if parsed is None or (parsed["number"] is None and not parsed["label"]):
                continue
        erase_label_preserving_wires(binary, item["bbox"], width)
    for polygon in refine_terminals(binary, components):
        cv2.fillConvexPoly(binary, polygon, 0)
    sk = skeletonize(binary > 0)
    ys, xs = np.nonzero(sk)
    pixels = {(int(x), int(y)) for x, y in zip(xs, ys)}
    adj = {p: set() for p in pixels}
    for x, y in pixels:
        for dx, dy in [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
            (1, 1),
            (-1, 1),
            (1, -1),
            (-1, -1),
        ]:
            q = x + dx, y + dy
            if q in pixels:
                if dx and dy and ((x + dx, y) in pixels or (x, y + dy) in pixels):
                    continue
                adj[(x, y)].add(q)
    prune_spurs(adj, width, components)
    warnings = separate_crossings(adj, binary, annotations, width)
    repairs, ghosts = repair_gaps(
        adj, components, annotation_mask, width, handwritten, repair, check
    )
    warnings += repairs
    membership = {}
    groups = []
    for p in sorted(adj):
        if p in membership:
            continue
        group = []
        stack = [p]
        index = len(groups)
        while stack:
            q = stack.pop()
            if q in membership:
                continue
            membership[q] = index
            group.append(q)
            stack.extend(adj[q])
        groups.append(group)
    return {
        "adj": adj,
        "membership": membership,
        "groups": groups,
        "warnings": warnings,
        "candidates": np.array(sorted(adj), dtype=float).reshape(-1, 2),
        "shape": (h, w),
        "stroke_width": width,
        "ghosts": ghosts,
        "terminals": {t.id: t.xy for c in components for t in c.terminals},
    }


def trace(
    image,
    components,
    texts=(),
    annotations=(),
    snap_scale=1.0,
    handwritten=False,
    prepared=None,
    diagnostics=None,
    check=lambda: None,
):
    cache = (
        prepared
        if prepared is not None
        else prepare_trace(image, components, texts, annotations, handwritten, check=check)
    )
    adj = cache["adj"]
    membership = cache["membership"]
    groups = cache["groups"]
    warnings = list(cache["warnings"])
    candidates = cache["candidates"]
    h, w = cache["shape"]
    nodes = []
    points = []
    segments = []
    anchors = {}
    used_groups = set()
    snapped = floating = off_axis = 0
    tolerance = min(40, max(12, min(w, h) * 0.04)) * snap_scale
    width = cache.get("stroke_width", 1.0)
    for c in components:
        check()
        for t in c.terminals:
            t.xy = cache.get("terminals", {}).get(t.id, t.xy)
        hits = []
        lead_tolerance = min(50, max(tolerance, math.dist(*[t.xy for t in c.terminals]) * 0.6))
        for index, t in enumerate(c.terminals):
            hits.append(terminal_hit(t, c.terminals[1 - index], candidates, lead_tolerance, width))
        # A same-group hit needs an actual outside-body path, not the same pixel.
        if all(hits) and membership[hits[0][0]] == membership[hits[1][0]]:
            if math.dist(hits[0][0], hits[1][0]) < max(3, width * 2):
                hits[1] = None
                warnings.append(("terminal_same_group", c.id))
            elif c.bbox[2] > c.bbox[0] and c.bbox[3] > c.bbox[1]:
                warnings.append(("possible_bypass", c.id))
        for t, hit in zip(c.terminals, hits):
            if hit is not None:
                p, offset = hit
                g = membership[p]
                used_groups.add(g)
                anchors[t.id] = p
                t.node = "n" + str(g + 1)
                snapped += 1
                if offset > max(2, width):
                    off_axis += 1
                    warnings.append(("off_axis_snap", c.id))
            else:
                floating += 1
                t.node = "isolated." + t.id
                c.confidence = min(c.confidence, 0.35)
                warnings.append(("uncertain_topology", c.id))
                nodes.append(Node(id=t.node))
                points.append(Point(id=t.id, xy=t.xy, node=t.node, kind="terminal"))
    for gi in sorted(used_groups):
        check()
        group = groups[gi]
        node = "n" + str(gi + 1)
        nodes.append(Node(id=node))
        critical = {p for p in group if len(adj[p]) != 2}
        critical.update(p for p in anchors.values() if membership[p] == gi)
        if not critical:
            critical.add(min(group))
        pointids = {p: f"p{len(points) + i + 1}" for i, p in enumerate(sorted(critical))}
        for p, id_ in pointids.items():
            points.append(
                Point(
                    id=id_,
                    xy=p,
                    node=node,
                    kind="junction" if len(adj[p]) >= 3 else "bend",
                )
            )
        traversed = set()
        for start in sorted(critical):
            check()
            for q in sorted(adj[start]):
                edge = frozenset([start, q])
                if edge in traversed:
                    continue
                path = [start, q]
                traversed.add(edge)
                prev = start
                current = q
                while current not in critical:
                    nxt = next(iter(adj[current] - {prev}))
                    traversed.add(frozenset([current, nxt]))
                    path.append(nxt)
                    prev, current = current, nxt
                approx = (
                    cv2.approxPolyDP(
                        np.array(path, dtype=np.float32).reshape(-1, 1, 2),
                        1.8 if handwritten else 1.2,
                        False,
                    )
                    .reshape(-1, 2)
                    .tolist()
                )
                if len(approx) < 2:
                    approx = [list(path[0]), list(path[-1])]
                segments.append(
                    Segment(
                        id=f"w{len(segments) + 1}",
                        from_=pointids[start],
                        to=pointids[current],
                        node=node,
                        polyline=approx,
                        confidence=0.6 if handwritten else 0.8,
                    )
                )
        for c in components:
            check()
            for t in c.terminals:
                p = anchors.get(t.id)
                if p is not None and membership[p] == gi:
                    points.append(Point(id=t.id, xy=t.xy, node=node, kind="terminal"))
                    axis = np.array(c.terminals[1].xy) - c.terminals[0].xy
                    delta = np.array(p) - t.xy
                    offset = abs(delta[0] * axis[1] - delta[1] * axis[0]) / max(
                        1, np.linalg.norm(axis)
                    )
                    segments.append(
                        Segment(
                            id=f"w{len(segments) + 1}",
                            from_=t.id,
                            to=pointids[p],
                            node=node,
                            polyline=[t.xy, p],
                            confidence=0.45
                            if offset > max(2, width)
                            else 0.6
                            if handwritten
                            else 0.85,
                        )
                    )
    if diagnostics is not None:
        diagnostics.update(
            terminals_snapped=snapped,
            terminals_floating=floating,
            off_axis_snaps=off_axis,
            gaps_bridged=sum(code == "gap_bridged" for code, _ in warnings),
            stroke_width=width,
            ghosts=cache.get("ghosts", []),
        )
    return nodes, WireGraph(points=points, segments=segments), warnings
