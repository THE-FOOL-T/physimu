"""Analytical test vectors; expectations are never obtained from the solver."""

import json
from pathlib import Path
from ..domains.circuit.netlist import (
    Netlist,
    Component,
    Terminal,
    Value,
    Node,
    Point,
    Segment,
    WireGraph,
    Polarity,
)

ROOT = Path(__file__).resolve().parents[2]


def circuit(name, specs, expected, *, transient=None):
    nodes = list(dict.fromkeys(n for _, _, a, b, _, _ in specs for n in (a, b)))
    coordinates = {n: (110 + 250 * (i % 3), 110 + 220 * (i // 3)) for i, n in enumerate(nodes)}
    cs = []
    points = []
    segments = []
    for i, (id_, kind, a, b, value, extra) in enumerate(specs):
        # Terminal geometry is illustrative; dedicated real-image overlays live in data/demos.
        x = 180 + (i % 4) * 145
        y = 180 + (i // 4) * 100
        ts = [
            Terminal(id=id_ + ".a", xy=(x - 30, y), node=a),
            Terminal(id=id_ + ".b", xy=(x + 30, y), node=b),
        ]
        c = Component(
            id=id_,
            type=kind,
            label=id_,
            bbox=(x - 25, y - 15, x + 25, y + 15),
            terminals=ts,
            value=Value(
                number=value,
                unit="V" if kind == "dc_source" else "F" if kind == "capacitor" else "ohm",
                status="given",
                source="user",
                confidence=1,
            ),
            confidence=1,
            **extra,
        )
        if kind == "dc_source":
            c.polarity = Polarity(positive_terminal=ts[0].id)
        cs.append(c)
        for t in ts:
            points.append(Point(id=t.id, xy=t.xy, node=t.node, kind="terminal"))
    for n in nodes:
        hub = Point(id="hub." + n, xy=coordinates[n], node=n, kind="junction")
        points.append(hub)
        for p in [p for p in points if p.node == n and p.id != hub.id]:
            segments.append(
                Segment(
                    id="w." + p.id,
                    from_=hub.id,
                    to=p.id,
                    node=n,
                    polyline=[hub.xy, p.xy],
                    confidence=1,
                )
            )
    net = Netlist(
        components=cs,
        nodes=[Node(id=n, is_ground=n == "g") for n in nodes],
        wire_graph=WireGraph(points=points, segments=segments),
    )
    result = {"name": name, "netlist": net.as_dict(), "expected": expected}
    if transient:
        result["transient"] = transient
    return result


def main():
    def s(id_, kind, a, b, v, **extra):
        return (id_, kind, a, b, v, extra)

    def v(value=12, a="p", b="g", id_="V1", **extra):
        return s(id_, "dc_source", a, b, value, **extra)

    def r(id_, a, b, value):
        return s(id_, "resistor", a, b, value)

    fixtures = [
        circuit(
            "single_resistor",
            [v(), r("R1", "p", "g", 6)],
            {"node_voltages": {"p": 12}, "currents": {"R1": 2, "V1": -2}},
        ),
        circuit(
            "series",
            [v(), r("R1", "p", "m", 4), r("R2", "m", "g", 8)],
            {"node_voltages": {"m": 8}, "currents": {"R1": 1, "R2": 1}},
        ),
        circuit(
            "parallel",
            [v(), r("R1", "p", "g", 6), r("R2", "p", "g", 3)],
            {"currents": {"V1": -6, "R1": 2, "R2": 4}},
        ),
        circuit(
            "divider",
            [v(10), r("R1", "p", "m", 2), r("R2", "m", "g", 3)],
            {"node_voltages": {"m": 6}, "currents": {"R1": 2}},
        ),
        circuit(
            "mixed",
            [v(), r("R1", "p", "m", 2), r("R2", "m", "g", 6), r("R3", "m", "g", 3)],
            {"node_voltages": {"m": 6}, "currents": {"V1": -3, "R2": 1, "R3": 2}},
        ),
        circuit(
            "balanced_bridge",
            [
                v(10),
                r("R1", "p", "a", 10),
                r("R2", "a", "g", 10),
                r("R3", "p", "b", 10),
                r("R4", "b", "g", 10),
                r("R5", "a", "b", 10),
            ],
            {"node_voltages": {"a": 5, "b": 5}, "currents": {"R5": 0, "V1": -1}},
        ),
        circuit(
            "unbalanced_bridge",
            [
                v(10),
                r("R1", "p", "a", 10),
                r("R2", "a", "g", 20),
                r("R3", "p", "b", 20),
                r("R4", "b", "g", 10),
                r("R5", "a", "b", 10),
            ],
            {
                "node_voltages": {"a": 40 / 7, "b": 30 / 7},
                "currents": {"R5": 1 / 7, "V1": -5 / 7},
            },
        ),
        circuit(
            "two_sources",
            [v(12, "p", "m"), v(3, "m", "g", "V2"), r("R1", "p", "g", 5)],
            {"node_voltages": {"p": 15, "m": 3}, "currents": {"R1": 3, "V2": -3}},
        ),
        circuit(
            "opposing_sources",
            [v(12), v(3, "m", "g", "V2"), r("R1", "p", "m", 3)],
            {"currents": {"R1": 3, "V1": -3, "V2": 3}},
        ),
        circuit(
            "current_source",
            [s("I1", "current_source", "g", "p", 2), r("R1", "p", "g", 5)],
            {"node_voltages": {"p": 10}, "currents": {"R1": 2}},
        ),
        circuit(
            "switch_open",
            [
                v(),
                s("S1", "switch", "p", "m", 1, switch_closed=False),
                r("R1", "m", "g", 10),
            ],
            {"currents": {"R1": 12 / (1e9 + 10)}},
        ),
        circuit(
            "switch_closed",
            [v(), s("S1", "switch", "p", "m", 1), r("R1", "m", "g", 10)],
            {"currents": {"R1": 12 / 10.001}},
        ),
        circuit(
            "bypassed_resistor",
            [v(), r("R1", "p", "g", 6), r("R2", "p", "p", 10)],
            {"currents": {"R1": 2, "R2": 0}, "bypassed": ["R2"]},
        ),
        circuit(
            "source_short",
            [v(), s("S1", "switch", "p", "g", 1)],
            {"currents": {"V1": -12 / 0.051, "S1": 12 / 0.051}, "short": True},
        ),
        circuit(
            "source_same_node",
            [v(10, "g", "g")],
            {"currents": {"V1": -200}, "short": True},
        ),
        circuit(
            "rc_charge",
            [v(10), r("R1", "p", "m", 1000), s("C1", "capacitor", "m", "g", 0.001)],
            {"node_voltages": {"m": 10}, "currents": {"R1": 0}},
            transient={
                "component": "C1",
                "duration": 5,
                "steps": 500,
                "final": 10 * (1 - (1 / 1.01) ** 500),
            },
        ),
        circuit(
            "rc_discharge",
            [
                r("R1", "p", "g", 1000),
                s("C1", "capacitor", "p", "g", 0.001, initial_voltage=10),
            ],
            {"node_voltages": {"p": 0}},
            transient={
                "component": "C1",
                "duration": 5,
                "steps": 500,
                "final": 10 * (1 / 1.01) ** 500,
            },
        ),
        circuit(
            "rl_step",
            [v(10), r("R1", "p", "m", 10), s("L1", "inductor", "m", "g", 1)],
            {"currents": {"R1": 10 / 10.000001}},
            transient={
                "component": "L1",
                "duration": 0.5,
                "steps": 500,
                "final": 1 - (1 / 1.01) ** 500,
            },
        ),
        circuit(
            "internal_resistance",
            [v(internal_resistance=2), r("R1", "p", "g", 4)],
            {"node_voltages": {"p": 8}, "currents": {"R1": 2, "V1": -2}},
        ),
        circuit(
            "closed_parallel_load",
            [v(), r("R1", "p", "g", 10), s("S1", "switch", "p", "g", 1)],
            {
                "currents": {"R1": (12 / (1 + 0.05 * (1000 + 0.1))) / 10},
                "short": True,
                "bypassed": ["R1"],
            },
        ),
        circuit(
            "shorted_capacitor",
            [v(), r("R1", "p", "g", 10), s("C1", "capacitor", "p", "p", 0.0001)],
            {"currents": {"C1": 0}, "bypassed": ["C1"]},
        ),
    ]
    (ROOT / "fixtures").mkdir(exist_ok=True)
    for f in fixtures:
        (ROOT / "fixtures" / f"{f['name']}.json").write_text(
            json.dumps(f, indent=2), encoding="utf-8"
        )
    (ROOT / "docs/schema.json").write_text(
        json.dumps(Netlist.model_json_schema(by_alias=True), indent=2), encoding="utf-8"
    )
    print(f"Wrote {len(fixtures)} analytical fixtures and JSON Schema")


if __name__ == "__main__":
    main()
