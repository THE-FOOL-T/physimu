"""Owner-supplied held-out evaluation; metrics remain null when ground truth is absent."""

import argparse
import collections
import json
from pathlib import Path
import statistics
import time
import networkx as nx
from ..domains.circuit.netlist import load
from ..core.preprocess import decode
from ..domains.circuit.engine import analyze_page
from ..domains.circuit.solver.mna import solve

ROOT = Path(__file__).resolve().parents[2]


def graph(net):
    g = nx.Graph()
    for n in net.nodes:
        g.add_node("n:" + n.id, type="node")
    for c in net.components:
        if c.virtual or c.disabled:
            continue
        g.add_node("c:" + c.id, type=c.type)
        for t in c.terminals:
            g.add_edge("c:" + c.id, "n:" + t.node)
    return g


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--eval", default=str(ROOT / "data/eval"))
    args = p.parse_args()
    summary = {}
    for split in ["printed", "handwritten"]:
        base = Path(args.eval) / split
        records = []
        for path in sorted((base / "images").glob("*")):
            if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
                continue
            goldpath = base / "netlists" / (path.stem + ".json")
            if not goldpath.is_file():
                raise ValueError("Gold netlist required: " + str(goldpath))
            gold = load(goldpath)
            start = time.perf_counter()
            out = analyze_page(
                decode(path.read_bytes()),
                style="handwritten" if split == "handwritten" else "auto",
            )
            from ..domains.circuit.netlist import Netlist

            pred = Netlist.model_validate(out["netlist"])
            gs = solve(gold)
            ps = out["solution"]
            matcher = nx.algorithms.isomorphism.GraphMatcher(
                graph(pred), graph(gold), node_match=lambda a, b: a["type"] == b["type"]
            )
            matched = matcher.is_isomorphic()
            electrical = False
            value_matches = 0
            status_matches = 0
            if matched:
                mapping = matcher.mapping
                diffs = []
                # Voltages are compared as differences relative to corresponding references.
                first = next(n.id for n in pred.nodes if "n:" + n.id in mapping)
                ref = mapping["n:" + first][2:]
                for n in pred.nodes:
                    if "n:" + n.id not in mapping:
                        continue
                    target = mapping["n:" + n.id][2:]
                    v = gs["node_voltages"][target] - gs["node_voltages"][ref]
                    pv = ps["node_voltages"][n.id] - ps["node_voltages"][first]
                    diffs.append(abs(v - pv) <= max(0.01, abs(v) * 0.01))
                electrical = all(diffs)
                for c in pred.components:
                    if "c:" + c.id not in mapping:
                        continue
                    target = next(g for g in gold.components if g.id == mapping["c:" + c.id][2:])
                    value_matches += abs((c.value.number or 0) - (target.value.number or 0)) <= max(
                        1e-12, abs(target.value.number or 0) * 0.01
                    )
                    status_matches += c.value.status == target.value.status
            pc = collections.Counter(c.type for c in pred.components if not c.virtual)
            gc = collections.Counter(c.type for c in gold.components if not c.virtual)
            records.append(
                {
                    "image": path.name,
                    "simulation_produced": bool(ps["components"]),
                    "graph_match": matched,
                    "electrical_correct": electrical,
                    "component_recall": sum((pc & gc).values()) / max(1, sum(gc.values())),
                    "value_fraction": value_matches / max(1, len(gold.components)),
                    "status_fraction": status_matches / max(1, len(gold.components)),
                    "seconds": time.perf_counter() - start,
                }
            )
        n = len(records)
        summary[split] = {
            "count": n,
            "metrics": {
                k: statistics.mean(r[k] for r in records) if n else None
                for k in [
                    "simulation_produced",
                    "graph_match",
                    "electrical_correct",
                    "component_recall",
                    "value_fraction",
                    "status_fraction",
                    "seconds",
                ]
            },
            "records": records,
            "status": "measured"
            if n
            else "HUMAN task: no frozen, independently labeled held-out examples supplied",
        }
    (ROOT / "docs/results.json").write_text(json.dumps(summary, indent=2))
    report = (
        "# End-to-end held-out evaluation\n\nMetrics are null when no frozen gold netlists are supplied; no scores are fabricated.\n\n```json\n"
        + json.dumps(summary, indent=2)
        + "\n```\n"
    )
    (ROOT / "docs/results.md").write_text(report, encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
