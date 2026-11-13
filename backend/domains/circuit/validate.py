"""Conservative topology checks and explicit, labeled fallback demonstrations."""

import json
from pathlib import Path
from .netlist import Netlist
from .solver.mna import VOLTAGE, solve


def fallback(width=800, height=500, path="", code="no_components"):
    p = Path(__file__).resolve().parents[3] / "fixtures/single_resistor.json"
    net = Netlist.model_validate(json.loads(p.read_text(encoding="utf-8"))["netlist"])
    net.image.path = ""  # A synthetic demonstration must never impersonate observed geometry.
    net.meta.degraded = True
    net.meta.provenance = "demo_fallback"
    for c in net.components:
        c.value.status = "assumed"
        c.value.source = "prior"
        c.value.confidence = 0
        c.confidence = 0
        c.virtual = True
    net.warn(code)
    net.warn("uncertain_topology")
    return net


def validate(net):
    net = net.model_copy(deep=True)
    if not net.components:
        return fallback()
    # All observed parts stay visible and editable. The solver can ground each
    # disconnected island; a broken trace must not disable a detected part.
    adj = {n.id: set() for n in net.nodes}
    for c in net.components:
        if c.disabled:
            continue
        if c.type == "switch" and not c.switch_closed:
            continue
        a, b = [t.node for t in c.terminals]
        adj[a].add(b)
        adj[b].add(a)
    groups = []
    seen = set()
    closed = set()
    for n in adj:
        if n in seen:
            continue
        group = set()
        stack = [n]
        while stack:
            q = stack.pop()
            if q in group:
                continue
            group.add(q)
            stack.extend(adj[q] - group)
        seen.update(group)
        cs = [
            c
            for c in net.components
            if not c.disabled
            and all(t.node in group for t in c.terminals)
            and not (c.type == "switch" and not c.switch_closed)
        ]
        groups.append(cs)
        sources = [c for c in cs if c.type in VOLTAGE]
        for source in sources:
            a, b = [t.node for t in source.terminals]
            edges = {n: set() for n in group}
            for c in cs:
                if c.id == source.id:
                    continue
                x, y = [t.node for t in c.terminals]
                edges[x].add(y)
                edges[y].add(x)
            reached = set()
            stack = [a]
            while stack:
                q = stack.pop()
                if q in reached:
                    continue
                reached.add(q)
                stack.extend(edges[q] - reached)
            if b in reached:
                closed.update(c.id for c in cs)
            else:
                net.warn("source_open_loop", source.id)
    if not closed:
        net.warn("no_closed_loop")
    for c in net.components:
        if c.id not in closed and not c.disabled:
            net.warn("not_connected", c.id)
    degree = {n.id: 0 for n in net.nodes}
    for c in net.components:
        if c.disabled:
            continue
        for t in c.terminals:
            degree[t.node] += 1
        if c.type in VOLTAGE and c.confidence < 0.95:
            net.warn("polarity_uncertain", c.id)
    for n, d in degree.items():
        if d < 2:
            net.warn("no_closed_loop", n)
    point_degree = {p.id: 0 for p in net.wire_graph.points}
    terminals = {t.id for c in net.components for t in c.terminals}
    for s in net.wire_graph.segments:
        point_degree[s.from_] += 1
        point_degree[s.to] += 1
    for id_, d in point_degree.items():
        if d == 1 and id_ not in terminals:
            net.warn("dangling_wire", id_)
    if any(
        w.code in {"uncertain_topology", "no_closed_loop", "not_connected"} for w in net.warnings
    ):
        net.meta.degraded = True
        net.meta.provenance = "partial"
    return net


def score(net):
    # Less dangling geometry and fewer disconnected component ends wins.
    return sum(
        3 if w.code == "no_closed_loop" else 2 if w.code == "uncertain_topology" else 1
        for w in validate(net).warnings
        if w.code in {"no_closed_loop", "uncertain_topology", "dangling_wire"}
    )


def safe_solve(net, **kwargs):
    try:
        result = solve(net, **kwargs)
        import math

        if not all(math.isfinite(v) for v in result["node_voltages"].values()):
            raise ValueError("Nonfinite solution")
        return net, result
    except (ValueError, ArithmeticError, RuntimeError) as exc:
        import logging

        logging.getLogger("circuit_sim.solver").exception("Solve failed: %s", type(exc).__name__)
        net.meta.degraded = True
        net.meta.provenance = "partial"
        net.warn("solve_failed")
        return net, {
            "node_voltages": {n.id: 0.0 for n in net.nodes},
            "components": {
                c.id: {
                    "v_drop": 0.0,
                    "current": 0.0,
                    "power": 0.0,
                    "internal_power": 0.0,
                    "internal_resistance": 0.0,
                    "deflection": 0,
                }
                for c in net.components
            },
            "segment_currents": {s.id: 0.0 for s in net.wire_graph.segments},
            "total_power_supplied": 0.0,
            "total_power_consumed": 0.0,
            "internal_power": 0.0,
            "equivalent_resistance": None,
            "short_circuit": {
                "detected": False,
                "sources": [],
                "bypassed": [],
                "short_paths": [],
                "ideal_current_infinite": False,
            },
            "state": {},
            "warnings": [w.model_dump() for w in net.warnings],
            "invariants": {
                "kcl": {},
                "max_kcl_error": None,
                "relative_power_error": None,
                "regularization_power": 0.0,
            },
        }
