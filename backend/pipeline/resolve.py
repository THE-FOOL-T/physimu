"""Constraint resolution using positive log parameters and null-space identifiability."""

import math
import numpy as np
from scipy.optimize import least_squares
from .netlist import Component, Terminal, Value, Node, Polarity
from .values import parse_constraints
from ..solver.mna import solve, VOLTAGE

PRIORS = {
    "resistor": 10,
    "rheostat": 10,
    "potentiometer": 10,
    "lamp": 10,
    "capacitor": 10e-6,
    "inductor": 0.1,
    "dc_source": 12,
    "battery": 12,
    "ac_source": 12,
    "current_source": 1,
    "switch": 1,
    "ammeter": 1e-6,
    "galvanometer": 1e-6,
    "voltmeter": 1e9,
}


def add_virtual_source(net):
    if any(c.type in VOLTAGE | {"current_source"} and not c.disabled for c in net.components):
        return
    if len(net.nodes) < 2:
        return
    # Prefer explicit A/B markers, otherwise the greatest graph distance in the component graph.
    a = next((n.id for n in net.nodes if n.label == "A"), None)
    b = next((n.id for n in net.nodes if n.label == "B"), None)
    if not a or not b:
        adj = {n.id: set() for n in net.nodes}
        for c in net.components:
            x, y = [t.node for t in c.terminals]
            adj[x].add(y)
            adj[y].add(x)
        best = (-1, None, None)
        for n in adj:
            queue = [(n, 0)]
            seen = {n}
            for q, d in queue:
                if d > best[0]:
                    best = (d, n, q)
                for r in adj[q] - seen:
                    seen.add(r)
                    queue.append((r, d + 1))
        a, b = best[1:]
    if not a or not b or a == b:
        a, b = [n.id for n in net.nodes[:2]]

    def xy(n):
        p = next((p for p in net.wire_graph.points if p.node == n), None)
        return p.xy if p else (30, 30)

    id_ = "Vtest"
    while any(c.id == id_ for c in net.components):
        id_ += "x"
    ts = [
        Terminal(id=id_ + ".a", node=a, xy=xy(a)),
        Terminal(id=id_ + ".b", node=b, xy=xy(b)),
    ]
    # Virtual geometry is offset from observed symbols and explicitly marked.
    net.components.append(
        Component(
            id=id_,
            type="dc_source",
            label="test",
            terminals=ts,
            virtual=True,
            bbox=(8, 8, 60, 34),
            polarity=Polarity(positive_terminal=id_ + ".a"),
            confidence=1,
            value=Value(number=10, unit="V", status="assumed", source="prior", confidence=0),
        )
    )
    net.warn("virtual_source", id_)


def resolve(net, keep_constraints=True):
    net = net.model_copy(deep=True)
    for con in parse_constraints(net.meta.problem_text):
        if con not in net.constraints:
            net.constraints.append(con)
    add_virtual_source(net)
    unknown = [
        c
        for c in net.components
        if not c.disabled
        and c.value.status != "user"
        and (c.value.number is None or keep_constraints and c.value.status == "solved")
    ]
    known_resistors = [
        c.value.number
        for c in net.components
        if c not in unknown
        and c.type in {"resistor", "rheostat", "potentiometer"}
        and c.value.number
        and c.value.number > 0
    ]
    e12 = np.array(
        [
            1.0,
            1.2,
            1.5,
            1.8,
            2.2,
            2.7,
            3.3,
            3.9,
            4.7,
            5.6,
            6.8,
            8.2,
            10.0,
            12.0,
            15.0,
            18.0,
            22.0,
            27.0,
            33.0,
            39.0,
            47.0,
            56.0,
            68.0,
            82.0,
            100.0,
        ]
    )
    near = float(np.median(known_resistors)) if known_resistors else 10.0
    resistor_prior = float(e12[np.argmin(abs(np.log(e12) - math.log(max(near, 1e-9))))])
    for c in unknown:
        c.value.number = (
            resistor_prior
            if c.type in {"resistor", "rheostat", "potentiometer"}
            else PRIORS.get(c.type, 10)
        )
        c.value.status = "assumed"
        c.value.source = "prior"
    net.warnings = [
        w
        for w in net.warnings
        if w.code != "inconsistent_constraints"
        and not (
            w.code == "assumed_value"
            and any(c.id == w.ref and c.value.status != "assumed" for c in net.components)
        )
    ]
    if not unknown:
        # Even fixed values can contradict given measurement constraints.
        if net.constraints:
            residual = _residual(net)
            if residual.size and np.max(np.abs(residual)) > 1e-4:
                net.warn(
                    "inconsistent_constraints",
                    net.constraints[int(np.argmax(np.abs(residual)))].target,
                )
        return net
    prior = np.log([max(c.value.number, 1e-12) for c in unknown])
    if net.constraints:

        def objective(x):
            for c, v in zip(unknown, x):
                c.value.number = float(np.exp(v))
            return _residual(net)

        rng = np.random.default_rng(42)
        candidates = []
        for start in [prior, *[prior + rng.normal(0, 1, len(prior)) for _ in range(3)]]:
            opt = least_squares(
                objective,
                start,
                bounds=(-30, 30),
                max_nfev=200,
                xtol=1e-12,
                ftol=1e-12,
                gtol=1e-12,
            )
            candidates.append(opt)
        opt = min(
            candidates,
            key=lambda o: (np.linalg.norm(o.fun), np.linalg.norm(o.x - prior)),
        )
        # Tiny prior regularization chooses sensible values only along unconstrained directions.
        regular = least_squares(
            lambda x: np.r_[objective(x), 1e-7 * (x - prior)],
            opt.x,
            bounds=(-30, 30),
            max_nfev=200,
            gtol=1e-12,
            ftol=1e-12,
            xtol=1e-12,
        )
        values = (
            regular.x
            if np.linalg.norm(objective(regular.x)) < max(1e-7, np.linalg.norm(opt.fun) + 1e-8)
            else opt.x
        )
        residual = objective(values)
        # Differentiate measurements only, excluding the prior penalty.
        J = np.empty((len(residual), len(unknown)))
        for j in range(len(unknown)):
            shifted = values.copy()
            shifted[j] += 1e-5
            J[:, j] = (objective(shifted) - residual) / 1e-5
        objective(values)
        _, singular, vh = np.linalg.svd(J, full_matrices=True)
        rank = int(np.sum(singular > max(1e-7, (singular[0] if len(singular) else 0) * 1e-7)))
        null = vh[rank:]
        free = np.sum(null**2, axis=0) if len(null) else np.zeros(len(unknown))
        inconsistent = bool(np.max(np.abs(residual), initial=0) > 1e-4)
        for j, c in enumerate(unknown):
            determined = free[j] < 1e-6 and not inconsistent
            c.value.status = "solved" if determined else "assumed"
            c.value.source = "constraint" if determined else "prior"
            c.value.confidence = 0.9 if determined else 0.2
        if inconsistent:
            target = net.constraints[int(np.argmax(np.abs(residual)))].target
            net.warn("inconsistent_constraints", target)
            c = next((c for c in net.components if c.id == target or c.label == target), None)
            if c:
                c.value.confidence = min(0.2, c.value.confidence)
    for c in unknown:
        if c.value.status == "assumed":
            net.warn("assumed_value", c.id)
    return net


def _residual(net):
    result = solve(net)
    residual = []
    byid = {c.id: c for c in net.components}
    byid.update({c.label: c for c in net.components if c.label})
    for con in net.constraints:
        c = byid.get(con.target)
        reading = result["components"].get(c.id) if c else None
        value = 0.0
        if con.target == "total" and con.type == "power":
            value = result["total_power_consumed"]
        elif con.target == "total" and con.type == "current":
            value = sum(
                abs(result["components"][source.id]["current"])
                for source in net.components
                if source.type in VOLTAGE and not source.disabled
            )
        elif con.type in {"current", "voltage", "power"} and reading:
            value = reading[{"current": "current", "voltage": "v_drop", "power": "power"}[con.type]]
            if con.value >= 0:
                value = abs(value)
        elif con.type == "voltage" and "-" in con.target:
            a, b = con.target.split("-", 1)
            labels = {n.label: n.id for n in net.nodes if n.label}
            value = result["node_voltages"].get(labels.get(a, a), 0) - result["node_voltages"].get(
                labels.get(b, b), 0
            )
        elif con.type == "equivalent_resistance":
            value = result["equivalent_resistance"] or 0
        elif con.type == "ratio" and "/" in con.target:
            a, b = con.target.split("/", 1)
            if a in byid and b in byid:
                value = (byid[a].value.number or 0) / max(byid[b].value.number or 1e-30, 1e-30)
        residual.append((value - con.value) / max(abs(con.value), 1.0))
    return np.array(residual)
