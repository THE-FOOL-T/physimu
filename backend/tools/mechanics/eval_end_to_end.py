"""Frozen HUMAN scene evaluation. Empty partitions have null metrics, never invented scores."""

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import subprocess
import time

import cv2
import numpy as np
from scipy.optimize import linear_sum_assignment

from ...domains.mechanics.engine import analyze_mechanics_page
from ...domains.mechanics.scene import Scene
from .common import NAMES, ROOT, FROZEN, read_labels, write_json
from .eval_detector import iou, score
from .gold import verify_frozen


PROTOCOL = dict(
    object_iou=0.5,
    scene_correspondence_iou=0.2,
    point_anchor_tolerance_px=12,
    parameter_text="exact SI numeric value and unit; missing/assumed values count as incorrect",
    measured_angle_tolerance_deg=3,
    trajectory="existing TypeScript solver; 121 equal-time samples over common horizon <=5s; displacements from initial state within .05m; capped end times within .02s",
    simulation_produced="reported independently; it does not establish correctness",
)


def object_box(obj):
    if "bbox" in obj:
        return obj["bbox"]
    if "center" in obj:
        x, y = obj["center"]
        r = obj["radius_px"]
        return [x - r, y - r, x + r, y + r]
    points = (
        [obj["tail"], obj["head"]]
        if "tail" in obj and "head" in obj
        else obj.get("polyline", obj.get("geometry", {}).get("points"))
    )
    if not points:
        return obj.get("geometry", {}).get("bbox")
    return [
        min(p[0] for p in points) - 3,
        min(p[1] for p in points) - 3,
        max(p[0] for p in points) + 3,
        max(p[1] for p in points) + 3,
    ]


def match_objects(prediction, gold):
    mapping = {}
    # IDs have no semantic role. Match only compatible types using native geometry.
    for group in ("bodies", "surfaces", "links", "pulleys", "forces", "annotations"):
        expected, actual = gold[group], prediction[group]
        if not expected or not actual:
            continue
        costs = np.full((len(expected), len(actual)), 2.0)
        for i, a in enumerate(expected):
            for j, b in enumerate(actual):
                x, y = object_box(a), object_box(b)
                if a.get("type") == b.get("type") and x and y:
                    costs[i, j] = 1 - iou(x, y)
                    pa, pb = (
                        a.get("geometry", {}).get("points"),
                        b.get("geometry", {}).get("points"),
                    )
                    if group == "annotations" and pa and pb and len(pa) == len(pb) == 1:
                        costs[i, j] = min(2.0, math.dist(pa[0], pb[0]) / 15)
        rows, cols = linear_sum_assignment(costs)
        for i, j in zip(rows, cols):
            if (
                costs[i, j] <= 0.8
            ):  # scene links/masks may shift; detection recall uses .5 separately
                mapping[expected[i]["id"]] = actual[j]["id"]
    return mapping


def value_paths(node, prefix=""):
    if isinstance(node, dict):
        if "number" in node and "unit" in node:
            if node["number"] is not None:
                yield prefix, node
        else:
            for key, value in node.items():
                if key not in {"warnings", "bindings", "constraints", "annotations", "meta"}:
                    yield from value_paths(value, (prefix + "." + key).strip("."))
    elif isinstance(node, list):
        for value in node:
            if isinstance(value, dict) and "id" in value:
                yield from value_paths(value, prefix + "." + value["id"])


def compare_scenes(prediction, gold):
    mapping = match_objects(prediction, gold)
    actual = dict(value_paths(prediction))
    parameters = []
    for path, expected in value_paths(gold):
        parts = path.split(".")
        if len(parts) > 1 and parts[0] in {"bodies", "surfaces", "links", "pulleys", "forces"}:
            parts[1] = mapping.get(parts[1], "__missing__")
        got = actual.get(".".join(parts))
        tolerance = (
            3 if expected["unit"] == "deg" and (not got or got["source"] == "geometry") else 0
        )
        correct = bool(
            got
            and got["number"] is not None
            and got["status"] != "assumed"
            and got["unit"] == expected["unit"]
            and abs(got["number"] - expected["number"]) <= tolerance
        )
        parameters.append(
            dict(
                path=path,
                correct=correct,
                expected=expected["number"],
                actual=got["number"] if got else None,
                tolerance=tolerance,
            )
        )
    attachments = []
    actual_links = {link["id"]: link for link in prediction["links"]}
    for link in gold["links"]:
        got = actual_links.get(mapping.get(link["id"]))
        expected = {mapping.get(link[e]["ref"], "__missing__") for e in ("a", "b")}
        attachments.append(bool(got and expected == {got[e]["ref"] for e in ("a", "b")}))
    actual_bodies = {b["id"]: b for b in prediction["bodies"]}
    for body in gold["bodies"]:
        got = actual_bodies.get(mapping.get(body["id"]))
        expected = mapping.get(body["on_surface"], "__missing__") if body["on_surface"] else None
        attachments.append(bool(got and got["on_surface"] == expected))
    return dict(
        archetype_correct=prediction["archetype"] == gold["archetype"],
        attachments=attachments,
        parameters=parameters,
        body_map={b["id"]: mapping[b["id"]] for b in gold["bodies"] if b["id"] in mapping},
    )


def trajectories(pairs):
    cli = ROOT / "frontend/node_modules/tsx/dist/cli.mjs"
    if not cli.is_file():
        raise ValueError(
            "Install pinned frontend dependencies to evaluate the product TypeScript solvers"
        )
    run = subprocess.run(
        ["node", str(cli), str(ROOT / "frontend/scripts/mechanics-evaluate.ts")],
        input=json.dumps(pairs),
        text=True,
        capture_output=True,
        cwd=ROOT,
        check=True,
        timeout=180,
    )
    return json.loads(run.stdout)


def aggregate(rows):
    def ratio(values):
        return sum(values) / len(values) if values else None

    timings = defaultdict(list)
    for row in rows:
        for key, value in row["timings"].items():
            if value is not None:
                timings[key].append(value)
    return dict(
        archetype_correct=ratio([r["archetype_correct"] for r in rows]),
        attachment_correct=ratio([v for r in rows for v in r["attachments"]]),
        parameter_correct=ratio([p["correct"] for r in rows for p in r["parameters"]]),
        trajectory_correct=ratio([r["trajectory_correct"] for r in rows]),
        simulation_produced=ratio([r["simulation_produced"] for r in rows]),
        seconds={
            key: dict(
                samples=len(values),
                total=sum(values),
                median=float(np.median(values)),
                p95=float(np.percentile(values, 95)),
            )
            for key, values in timings.items()
        }
        or None,
    )


def read_gold_scene(path):
    # Freeze verification validates input, but a human author may omit defaults.
    raw = json.loads(Path(path).read_text(encoding="utf-8"))["scene"]
    return Scene.model_validate(raw).model_dump(mode="json", by_alias=True)


def evaluate(root=FROZEN, *, analyzer=analyze_mechanics_page):
    records = verify_frozen(root)
    report = dict(domain="mechanics", origin="real", protocol=PROTOCOL, partitions={})
    for style in ("printed", "handwritten"):
        selected = [r for r in records if r["style"] == style]
        rows = []
        pairs = []
        ground = {}
        predictions = {}
        for record in selected:
            gold = read_gold_scene(record["gold"])
            start = time.perf_counter()
            result = analyzer(cv2.imread(record["image"]), dict(style=style))
            row = compare_scenes(result["scene"], gold)
            row.update(
                sha256=record["sha256"],
                timings={**result["timings"], "wall": time.perf_counter() - start},
                provenance=result["provenance"],
            )
            rows.append(row)
            pairs.append(dict(prediction=result["scene"], gold=gold, body_map=row["body_map"]))
            if "labels" in record:
                ground[record["sha256"]] = read_labels(
                    Path(record["labels"]), gold["image"]["width"], gold["image"]["height"]
                )
                predictions[record["sha256"]] = [
                    (NAMES.index(d["type"]), d["confidence"], d["bbox"])
                    for d in result["diagnostics"]["detections"]
                    if d["type"] in NAMES
                ]
        if pairs:
            for row, trajectory in zip(rows, trajectories(pairs)):
                row.update(trajectory)
        classes = (
            score(ground, predictions)
            if ground
            else {name: dict(support=None, recall=None) for name in NAMES}
        )
        report["partitions"][style] = dict(
            images=len(rows),
            frozen=bool(rows),
            metrics={
                **aggregate(rows),
                "object_recall": {name: r["recall"] for name, r in classes.items()},
            },
            classes=classes,
            records=rows,
            human_task=None
            if rows
            else "Supply independently HUMAN-reviewed, source-separated frozen scenes and labels. No real metric was measured.",
        )
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=FROZEN)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = evaluate(args.root)
    if args.out:
        write_json(args.out, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
