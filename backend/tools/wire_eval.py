"""Isolate tracing changes on the five recorded WP-A rasters/detections/texts."""

import base64
import copy
import json
import time
from pathlib import Path

import cv2
import numpy as np

from ..domains.circuit.netlist import Netlist, Component
from ..domains.circuit.wires import prepare_trace, trace
from ..domains.circuit.validate import validate, score, safe_solve

ROOT = Path(__file__).resolve().parents[2]


def stats(net, solution):
    return {
        "nodes": len(net.nodes),
        "parts": len(net.components),
        "disabled": sum(c.disabled for c in net.components),
        "provenance": net.meta.provenance,
        "nonzero_current": any(abs(v["current"]) > 1e-8 for v in solution["components"].values()),
        "score": score(net),
        "warnings": [w.model_dump() for w in net.warnings],
    }


def main():
    reports = []
    out = ROOT / ".cache/round3/wires"
    out.mkdir(parents=True, exist_ok=True)
    with (ROOT / ".cache/round3/after.jsonl").open(encoding="utf-8") as stream:
        for index, line in enumerate(stream):
            item = json.loads(line)
            result = item["result"]
            old = Netlist.model_validate(result["netlist"])
            image = cv2.imdecode(
                np.frombuffer(base64.b64decode(result["source_image"].split(",", 1)[1]), np.uint8),
                cv2.IMREAD_COLOR,
            )
            texts = result.get("diagnostics", {}).get("texts", [])
            # These five selected v2 runs contain no extended annotation boxes.
            annotations = []
            candidates = []
            start = time.perf_counter()
            for alternative, repair in [(False, False), (False, True), (True, True)]:
                cs = [Component.model_validate(c.model_dump()) for c in old.components]
                for c in cs:
                    c.disabled = False  # Undo the old validator's automatic exclusions.
                prepared = prepare_trace(
                    image,
                    cs,
                    texts,
                    annotations,
                    alternative=alternative,
                    repair=repair,
                )
                diagnostic = {"alternative_threshold": alternative, "repair": repair}
                nodes, graph, warnings = trace(
                    image,
                    cs,
                    texts,
                    annotations,
                    prepared=prepared,
                    diagnostics=diagnostic,
                )
                net = Netlist(
                    image=old.image,
                    components=cs,
                    nodes=nodes,
                    wire_graph=graph,
                    meta=copy.deepcopy(old.meta),
                )
                net.meta.degraded = False
                net.meta.provenance = "extracted"
                for code, ref in warnings:
                    net.warn(code, ref)
                net = validate(net)
                candidates.append((net, diagnostic))
            net, diagnostic = min(candidates, key=lambda candidate: score(candidate[0]))
            net, solution = safe_solve(net)
            report = {
                "image": item["image"],
                "before": stats(old, result["solution"]),
                "after": stats(net, solution),
                "trace": diagnostic,
                "seconds": time.perf_counter() - start,
                "scope": "Tracing-only replay on identical WP-A detections/texts; no gold topology accuracy.",
            }
            reports.append(report)
            view = cv2.addWeighted(image, 0.55, np.full_like(image, 255), 0.45, 0)
            for segment in net.wire_graph.segments:
                color = (220, 100, 20) if segment.confidence >= 0.6 else (160, 0, 180)
                cv2.polylines(
                    view,
                    [np.array(segment.polyline).round().astype(np.int32)],
                    False,
                    color,
                    1,
                )
            for c in net.components:
                for t in c.terminals:
                    xy = tuple(map(round, t.xy))
                    cv2.circle(view, xy, 3, (0, 140, 255), 1)
                cv2.putText(
                    view,
                    c.id,
                    tuple(map(round, c.terminals[0].xy)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.35,
                    (140, 30, 0),
                    1,
                )
            cv2.imwrite(str(out / f"case-{index + 1:03}.png"), view)
            case = ROOT / f"docs/cases/case-{index + 1:03}.md"
            content = case.read_text(encoding="utf-8").split("\n## WP-B tracing replay")[0]
            content += "\n## WP-B tracing replay\n\nSame WP-A detections and OCR; no detector/OCR rerun or gold topology claim. "
            content += (
                f"Wire overlay: `.cache/round3/wires/case-{index + 1:03}.png` (local only).\n\n"
            )
            content += "```json\n" + json.dumps(report, ensure_ascii=False, indent=2) + "\n```\n"
            case.write_text(content, encoding="utf-8")
            print(
                json.dumps({k: report[k] for k in ("image", "after", "trace", "seconds")}),
                flush=True,
            )
    (ROOT / "docs/wire_round3.json").write_text(
        json.dumps(reports, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
