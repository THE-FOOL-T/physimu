"""DC and backward-Euler MNA with explicit repair and electrical invariants."""

import math
import numpy as np
from .flow import segment_currents, decompose_paths

VOLTAGE = {"dc_source", "battery", "ac_source"}
RESISTIVE = {"resistor", "rheostat", "potentiometer", "lamp", "fuse"}
METERS = {"ammeter", "galvanometer"}
SUPPORTED = (
    VOLTAGE
    | RESISTIVE
    | METERS
    | {"switch", "voltmeter", "capacitor", "inductor", "current_source", "ground"}
)


def low_path(net, a, b, exclude=None):
    if a == b:
        return []
    adj = {n.id: [] for n in net.nodes}
    for c in net.components:
        if c.disabled or c.id == exclude:
            continue
        if (c.type == "switch" and c.switch_closed) or c.type in METERS:
            x, y = [t.node for t in c.terminals]
            adj[x].append((y, c.id))
            adj[y].append((x, c.id))
    queue = [(a, [])]
    seen = {a}
    for p, path in queue:
        for q, id_ in adj[p]:
            if q == b:
                return path + [id_]
            if q not in seen:
                seen.add(q)
                queue.append((q, path + [id_]))
    return None


def solve(net, *, dt=None, state=None, repair=True):
    state = state or {}
    warnings = [w.model_dump() for w in net.warnings]

    def warn(code, ref=None):
        w = {"code": code, "ref": ref, "message_key": "warn." + code}
        if w not in warnings:
            warnings.append(w)

    cs = [c for c in net.components if not c.disabled]
    source = next((c for c in cs if c.type in VOLTAGE), None)
    ground = next((n.id for n in net.nodes if n.is_ground), None)
    if ground is None:
        ground = (
            source.terminals[
                0
                if source.polarity and source.polarity.positive_terminal == source.terminals[1].id
                else 1
            ].node
            if source
            else (net.nodes[0].id if net.nodes else None)
        )
        warn("assumed_ground", ground)
    ids = [n.id for n in net.nodes if n.id != ground]
    index = {n: i for i, n in enumerate(ids)}
    vs = [c for c in cs if c.type in VOLTAGE or (c.type == "inductor" and dt)]
    branches = {c.id: len(ids) + i for i, c in enumerate(vs)}
    size = len(ids) + len(vs)
    A = np.zeros((size, size))
    z = np.zeros(size)
    conductance = {}
    history = {}
    emf = {}
    internal = {}
    shorts = []
    bypassed = []
    connectivity = {n.id: set() for n in net.nodes}

    def add(row, col, x):
        if row is not None and col is not None:
            A[row, col] += x

    def inj(a, b, i):
        if a is not None:
            z[a] -= i
        if b is not None:
            z[b] += i

    def stamp_g(a, b, g):
        add(a, a, g)
        add(b, b, g)
        add(a, b, -g)
        add(b, a, -g)

    for c in cs:
        na, nb = [t.node for t in c.terminals]
        a = index.get(na)
        b = index.get(nb)
        value = c.value.number if c.value.number is not None else (10 if c.type in RESISTIVE else 1)
        if c.type not in SUPPORTED:
            warn("unsupported_component", c.id)
            continue
        path = low_path(net, na, nb, c.id)
        if path is not None and c.type not in VOLTAGE | METERS | {"switch", "ground"}:
            bypassed.append(c.id)
        g = 0.0
        h = 0.0
        if c.type in RESISTIVE:
            g = 1 / max(abs(value), 1e-9)
        elif c.type == "switch":
            g = 1 / (0.001 if c.switch_closed else 1e9)
        elif c.type in METERS:
            g = 1e6
        elif c.type == "voltmeter":
            g = 1e-9
        elif c.type == "inductor" and not dt:
            g = 1e6
        elif c.type == "capacitor" and dt:
            g = max(value, 1e-15) / dt
            h = -g * state.get(c.id, c.initial_voltage)
        elif c.type == "current_source":
            h = value * (
                -1 if c.polarity and c.polarity.positive_terminal == c.terminals[1].id else 1
            )
        if g:
            stamp_g(a, b, g)
        if h:
            inj(a, b, h)
        conductance[c.id] = g
        history[c.id] = h
        if g or c.id in branches:
            connectivity[na].add(nb)
            connectivity[nb].add(na)
        if c.id in branches:
            k = branches[c.id]
            add(a, k, 1)
            add(b, k, -1)
            add(k, a, 1)
            add(k, b, -1)
            if c.type == "inductor":
                r = max(value, 1e-15) / dt
                A[k, k] = -r
                z[k] = -r * state.get(c.id, c.initial_current)
            else:
                r = c.internal_resistance or 0.0
                if path is not None:
                    if c.internal_resistance is None or c.internal_resistance == 0:
                        r = 0.05
                    shorts.append(c.id)
                    warn("source_short", c.id)
                e = value * (
                    -1 if c.polarity and c.polarity.positive_terminal == c.terminals[1].id else 1
                )
                A[k, k] = -r
                z[k] = e
                emf[c.id] = e
                internal[c.id] = r
                if c.type == "ac_source":
                    warn("unsupported_ac", c.id)
    # Ground each disconnected conductive island, not every node. Include leakage in diagnostics.
    reached = set()
    leak = {}
    if ground is not None:
        stack = [ground]
        while stack:
            p = stack.pop()
            if p in reached:
                continue
            reached.add(p)
            stack.extend(connectivity[p] - reached)
    for n in ids:
        if n not in reached:
            A[index[n], index[n]] += 1e-9
            leak[n] = 1e-9
            warn("floating_node", n)
            stack = [n]
            while stack:
                p = stack.pop()
                if p in reached:
                    continue
                reached.add(p)
                stack.extend(connectivity[p] - reached)
    try:
        x = np.linalg.solve(A, z) if size else np.array([])
    except np.linalg.LinAlgError:
        if not repair:
            raise
        # Inconsistent ideal source cycles receive explicit series resistance.
        for c in vs:
            if c.type in VOLTAGE and not internal[c.id]:
                A[branches[c.id], branches[c.id]] = -0.001
                internal[c.id] = 0.001
                warn("conflicting_sources", c.id)
        x = np.linalg.lstsq(A, z, rcond=1e-15)[0]
    voltages = {n.id: (0.0 if n.id == ground else float(x[index[n.id]])) for n in net.nodes}
    readings = {}
    kcl = {n.id: 0.0 for n in net.nodes}
    new_state = {}
    consumed = 0.0
    supplied = 0.0
    losses = 0.0
    for c in cs:
        na, nb = [t.node for t in c.terminals]
        v = voltages[na] - voltages[nb]
        i = (
            float(x[branches[c.id]])
            if c.id in branches
            else conductance.get(c.id, 0) * v + history.get(c.id, 0)
        )
        p = v * i
        loss = i * i * internal.get(c.id, 0)
        losses += loss
        readings[c.id] = {
            "v_drop": v,
            "current": i,
            "power": p,
            "internal_power": loss,
            "internal_resistance": internal.get(c.id, 0),
            "deflection": int(np.sign(i)),
        }
        consumed += max(0, p)
        supplied += max(0, -p)
        kcl[na] += i
        kcl[nb] -= i
        if c.type == "capacitor":
            new_state[c.id] = v
        if c.type == "inductor":
            new_state[c.id] = i
    leak_power = 0.0
    for n, g in leak.items():
        current = g * voltages[n]
        kcl[n] += current
        if ground is not None:
            kcl[ground] -= current
        leak_power += g * voltages[n] ** 2
    consumed += losses + leak_power
    supplied += losses
    currents, flow_warnings = segment_currents(net, readings)
    warnings += flow_warnings
    path_sources = [c.id for c in cs if c.type in VOLTAGE] if shorts or bypassed else []
    paths = decompose_paths(net, readings, currents, path_sources)
    scale = max(consumed, supplied, 1e-30)
    kcl_error = max((abs(v) for v in kcl.values()), default=0)
    power_error = abs(consumed - supplied) / scale
    if kcl_error > max(
        1e-10, max((abs(r["current"]) for r in readings.values()), default=0) * 1e-9
    ):
        warn("kcl_residual")
    if power_error > 1e-9:
        warn("power_residual")
    req = None
    if source and abs(readings[source.id]["current"]) > 1e-15:
        req = abs(readings[source.id]["v_drop"] / readings[source.id]["current"])
    return {
        "node_voltages": voltages,
        "components": readings,
        "segment_currents": currents,
        "total_power_supplied": supplied,
        "total_power_consumed": consumed,
        "internal_power": losses,
        "equivalent_resistance": req,
        "short_circuit": {
            "detected": bool(shorts or bypassed),
            "sources": shorts,
            "bypassed": bypassed,
            "short_paths": paths,
            "ideal_current_infinite": bool(shorts),
        },
        "state": new_state,
        "warnings": warnings,
        "invariants": {
            "kcl": kcl,
            "max_kcl_error": kcl_error,
            "relative_power_error": power_error,
            "regularization_power": leak_power,
        },
    }


def transient(net, duration=None, steps=None, state=None):
    rs = [max(c.value.number or 10, 1e-6) for c in net.components if c.type in RESISTIVE]
    taus = [
        (c.value.number or 1e-6) * (max(rs) if rs else 10)
        for c in net.components
        if c.type == "capacitor"
    ]
    taus += [
        (c.value.number or 0.001) / (min(rs) if rs else 10)
        for c in net.components
        if c.type == "inductor"
    ]
    duration = duration or 5 * max(taus, default=1)
    required = math.ceil(duration / max(min(taus, default=1) / 100, 1e-15))
    limited = steps is None and required > 5000
    steps = max(2, min(5000, steps if steps is not None else required))
    dt = duration / steps
    state = dict(
        state
        or {
            c.id: c.initial_voltage if c.type == "capacitor" else c.initial_current
            for c in net.components
            if c.type in {"capacitor", "inductor"}
        }
    )
    # Include t=0 with exact declared stored state; first numerical sample is at dt.
    samples = [{"time": 0.0, "state": dict(state)}]
    for k in range(1, steps + 1):
        s = solve(net, dt=dt, state=state)
        state = s["state"]
        samples.append({"time": k * dt, "state": dict(state), "components": s["components"]})
    if limited:
        s["warnings"].append(
            {
                "code": "time_step_limited",
                "ref": None,
                "message_key": "warn.time_step_limited",
            }
        )
    return {
        "duration": duration,
        "dt": dt,
        "samples": samples,
        "solution": s,
        "steady_state": solve(net),
    }
