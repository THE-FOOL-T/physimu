"""Map terminal injections to signed currents on a minimum-length wire tree."""

import math


def segment_currents(net, components):
    points = {p.id: p for p in net.wire_graph.points}
    result = {s.id: 0.0 for s in net.wire_graph.segments}
    warnings = []
    for node in net.nodes:
        ps = [p for p in points.values() if p.node == node.id]
        if not ps:
            continue
        parent = {p.id: p.id for p in ps}

        def find(p):
            while parent[p] != p:
                parent[p] = parent[parent[p]]
                p = parent[p]
            return p

        adj = {p.id: [] for p in ps}
        edges = [s for s in net.wire_graph.segments if s.node == node.id]

        def length(s):
            return sum(math.dist(a, b) for a, b in zip(s.polyline, s.polyline[1:]))

        for s in sorted(edges, key=lambda s: (length(s), s.id)):
            a, b = find(s.from_), find(s.to)
            if a == b:
                warnings.append({"code": "wire_loop", "ref": s.id, "message_key": "warn.wire_loop"})
                continue
            parent[a] = b
            adj[s.from_].append((s.to, s, 1))
            adj[s.to].append((s.from_, s, -1))
        injections = {p.id: 0.0 for p in ps}
        for c in net.components:
            if c.id not in components:
                continue
            for k, t in enumerate(c.terminals):
                if t.node == node.id:
                    p = min(ps, key=lambda p: math.dist(p.xy, t.xy))
                    injections[p.id] += components[c.id]["current"] * (-1 if k == 0 else 1)
        seen = set()

        def visit(p, prev):
            seen.add(p)
            total = injections[p]
            for q, s, sign in adj[p]:
                if q == prev:
                    continue
                sub = visit(q, p)
                result[s.id] = -sub * sign
                total += sub
            return total

        for p in ps:
            if p.id not in seen:
                imbalance = visit(p.id, None)
                if abs(imbalance) > 1e-7:
                    warnings.append(
                        {
                            "code": "wire_imbalance",
                            "ref": node.id,
                            "message_key": "warn.wire_imbalance",
                        }
                    )
    return result, warnings


def decompose_paths(net, readings, currents, source_ids):
    """Residual-flow decomposition through actual wires AND component terminals."""
    points = {p.id: p for p in net.wire_graph.points}

    def terminal(t):
        ps = [p for p in points.values() if p.node == t.node]
        return min(ps, key=lambda p: math.dist(p.xy, t.xy)).id if ps else "node:" + t.node

    edges = []
    for s in net.wire_graph.segments:
        edges.append([s.from_, s.to, currents[s.id], s.id, False])
    for c in net.components:
        if c.id in readings and c.id not in source_ids:
            edges.append(
                [
                    terminal(c.terminals[0]),
                    terminal(c.terminals[1]),
                    readings[c.id]["current"],
                    c.id,
                    True,
                ]
            )
    output = []
    for src in [c for c in net.components if c.id in source_ids]:
        flip = src.polarity and src.polarity.positive_terminal == src.terminals[1].id
        start = terminal(src.terminals[1 if flip else 0])
        end = terminal(src.terminals[0 if flip else 1])
        residual = []
        for a, b, i, id_, component in edges:
            if abs(i) > 1e-12:
                residual.append([b if i < 0 else a, a if i < 0 else b, abs(i), id_, component])
        total = abs(readings[src.id]["current"])
        for _ in range(100):

            def search(p, seen):
                if p == end:
                    return []
                for j, e in sorted(enumerate(residual), key=lambda x: -x[1][2]):
                    if e[0] == p and e[1] not in seen and e[2] > max(1e-12, total * 0.0001):
                        tail = search(e[1], seen | {e[1]})
                        if tail is not None:
                            return [j] + tail
                return None

            path = search(start, {start})
            if not path:
                break
            amount = min(residual[j][2] for j in path)
            for j in path:
                residual[j][2] -= amount
            output.append(
                {
                    "source": src.id,
                    "current": amount,
                    "segments": [residual[j][3] for j in path if not residual[j][4]],
                    "components": [residual[j][3] for j in path if residual[j][4]],
                }
            )
            if sum(p["current"] for p in output if p["source"] == src.id) >= total * 0.99:
                break
    return output
