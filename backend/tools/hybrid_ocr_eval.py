"""Offline legacy/hybrid comparison. Synthetic and real-image evidence stay separate.

Requires explicit local hybrid model configuration. Writes only to --out. Real
images without reviewed text/value/netlist gold never receive accuracy scores.
"""

import argparse
from contextlib import contextmanager
import copy
import json
import os
from pathlib import Path
import socket
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.optimize import linear_sum_assignment

from ..config import ROOT, load_config
from ..pipeline.associate import associate
from ..pipeline.netlist import Component, Terminal
from ..pipeline.ocr_hybrid.normalize import normalize, parse
from ..pipeline.ocr_regions import area, intersection
from ..pipeline.text import read_text


@contextmanager
def offline():
    original = socket.socket.connect
    attempts = []

    def denied(sock, address):
        attempts.append(str(address))
        raise RuntimeError("Network forbidden during offline OCR evaluation")

    socket.socket.connect = denied
    try:
        yield attempts
    finally:
        socket.socket.connect = original


def metrics(items, gold):
    """One-to-one box matching; assignment coverage is separate from precision."""
    matches = {}
    if items and gold:
        overlaps = np.array(
            [
                [
                    intersection(g["bbox"], i["bbox"])
                    / max(1, area(g["bbox"]) + area(i["bbox"]) - intersection(g["bbox"], i["bbox"]))
                    for i in items
                ]
                for g in gold
            ]
        )
        rows, columns = linear_sum_assignment(1 - overlaps)
        matches = {r: items[c] for r, c in zip(rows, columns) if overlaps[r, c] >= 0.5}
    assigned = correct = covered = exact = wrong = value_correct = ambiguous_correct = 0
    value_errors = {}
    for row, label in enumerate(gold):
        item = matches.get(row, {})
        selected = item.get("assigned_to")
        target = label.get("component_id")
        exact += bool(
            item
            and normalize(item["text"]).replace(" ", "")
            == normalize(label["text"]).replace(" ", "")
        )
        assigned += bool(selected)
        covered += bool(selected and target)
        correct += bool(selected and selected == target)
        wrong += bool(selected and selected != target)
        ambiguous_correct += bool(
            item and label.get("ambiguous") and not selected and item.get("reason") == "ambiguous"
        )
        expected = parse(label["text"])
        actual = item.get("parsed") or parse(item.get("text", ""))
        if (
            expected
            and expected["unit"]
            and actual
            and actual["number"] is not None
            and actual["unit"] == expected["unit"]
        ):
            error = abs(actual["number"] - expected["number"])
            value_errors.setdefault(expected["unit"], []).append(error)
            value_correct += bool(
                selected == target
                and target
                and error <= max(1e-12, abs(expected["number"]) * 1e-6)
            )
    correct_regions = correct
    matched_ids = {id(i) for i in matches.values()}
    for item in items:
        if id(item) in matched_ids or not item.get("assigned_to"):
            continue
        # A separately detected R1 inside 'R1 = 10 Ω' can be valid additional
        # name evidence. It does not increase coverage or value accuracy.
        supported_subspan = any(
            item["assigned_to"] == label.get("component_id")
            and intersection(item["bbox"], label["bbox"]) / max(1, area(item["bbox"])) >= 0.5
            and normalize(item["text"]).replace(" ", "")
            in normalize(label["text"]).replace(" ", "")
            for label in gold
        )
        assigned += 1
        correct += bool(supported_subspan)
        wrong += not supported_subspan
    expected_values = sum(
        bool((v := parse(g["text"])) and v["unit"] and g.get("component_id")) for g in gold
    )
    expected_links = sum(bool(g.get("component_id")) for g in gold)
    return {
        "regions": len(gold),
        "ocr_exact_normalized_text_accuracy": exact / len(gold) if gold else None,
        "association_precision": correct / assigned if assigned else None,
        "association_coverage": covered / expected_links if expected_links else None,
        "association_recall": correct_regions / expected_links if expected_links else None,
        "false_assignments": wrong,
        "false_assignment_rate_among_assigned": wrong / assigned if assigned else None,
        "correct_component_value_assignment_rate": value_correct / expected_values
        if expected_values
        else None,
        "mean_absolute_SI_value_error_by_unit": {
            unit: float(np.mean(errors)) for unit, errors in value_errors.items()
        },
        "ambiguous_correctly_unassigned": ambiguous_correct,
    }


def synthetic():
    import matplotlib

    latin = Path(matplotlib.get_data_path()) / "fonts/ttf/DejaVuSans.ttf"
    bengali = ROOT / "frontend/public/fonts/NotoSansBengali.ttf"
    labels = ["R1 = 10 Ω", "R2 = 20 Ω", "R3 = 4.7 kΩ", "12 V", "১০ ওহম", "100 µF"]
    page = Image.new("RGB", (1000, 480), "white")
    draw = ImageDraw.Draw(page)
    gold, components = [], []
    kinds = ["resistor", "resistor", "resistor", "dc_source", "resistor", "capacitor"]
    ids = ["R1", "R2", "R3", "V1", "R4", "C1"]
    for index, (label, kind, id_) in enumerate(zip(labels, kinds, ids)):
        x, y = 65 + index % 3 * 330, 70 + index // 3 * 240
        font = ImageFont.truetype(
            str(bengali if any("\u0980" <= c <= "\u09ff" for c in label) else latin), 24
        )
        box = draw.textbbox((x, y), label, font=font)
        draw.text((x, y), label, font=font, fill="black")
        cx = (box[0] + box[2]) / 2
        cy = box[3] + 40
        bbox = (cx - 30, cy - 10, cx + 30, cy + 10)
        # Explicit synthetic bodies, isolated from text to measure recognition
        # and association separately from detector quality.
        draw.rectangle(bbox, outline="black", width=2)
        components.append(
            Component(
                id=id_,
                type=kind,
                bbox=bbox,
                terminals=[
                    Terminal(id=id_ + ".a", xy=(cx - 30, cy), node="pending"),
                    Terminal(id=id_ + ".b", xy=(cx + 30, cy), node="pending"),
                ],
            )
        )
        gold.append({"text": label, "bbox": list(box), "component_id": id_})
    return cv2.cvtColor(np.asarray(page), cv2.COLOR_RGB2BGR), components, gold


def recorded(path, hybrid):
    total = assigned = correct = wrong = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        components = [Component.model_validate(c) for c in row["components"]]
        items = copy.deepcopy(row["texts"])
        if hybrid:
            for item in items:
                item["ocr_backend"] = "hybrid"
        associate(components, items)
        for item in items:
            if not item.get("target_component"):
                continue
            total += 1
            if item.get("assigned_to"):
                assigned += 1
                if item["assigned_to"] == item["target_component"]:
                    correct += 1
                else:
                    wrong += 1
    return {
        "scope": "Frozen OCR association replay; no new OCR or value gold",
        "annotated": total,
        "assigned": assigned,
        "correct": correct,
        "wrong": wrong,
        "precision": correct / assigned if assigned else None,
        "coverage": assigned / total if total else None,
        "recall": correct / total if total else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=".cache/hybrid-evaluation.json")
    parser.add_argument("--real-count", type=int, default=0)
    args = parser.parse_args()
    previous = os.environ.get("CIRCUIT_OCR_BACKEND")
    report = {
        "synthetic": {},
        "orientation_smoke": [],
        "recorded_real_association": {},
        "real_images": [],
        "network_attempts": [],
    }
    try:
        with offline() as attempts:
            image, components, gold = synthetic()
            for backend in ("legacy", "hybrid"):
                os.environ["CIRCUIT_OCR_BACKEND"] = backend
                warm_started = time.perf_counter()
                read_text(image, components=components, deadline=time.monotonic() + 120)
                warm_seconds = time.perf_counter() - warm_started
                diagnostic = {}
                started = time.perf_counter()
                items, warnings = read_text(image, components=components, diagnostics=diagnostic)
                associate(copy.deepcopy(components), items)
                report["synthetic"][backend] = {
                    **metrics(items, gold),
                    "seconds": time.perf_counter() - started,
                    "warmup_seconds": warm_seconds,
                    "warnings": warnings,
                    "diagnostics": diagnostic,
                    "texts": items,
                }
                report["recorded_real_association"][backend] = recorded(
                    ROOT / "data/eval/real_images_association.jsonl", backend == "hybrid"
                )
                print(
                    json.dumps({"backend": backend, **metrics(items, gold)}, ensure_ascii=True),
                    flush=True,
                )
            import matplotlib

            font = ImageFont.truetype(
                str(Path(matplotlib.get_data_path()) / "fonts/ttf/DejaVuSans.ttf"), 30
            )
            crop = Image.new("RGB", (180, 90), "white")
            ImageDraw.Draw(crop).text((50, 25), "6 Ω", font=font, fill="black")
            os.environ["CIRCUIT_OCR_BACKEND"] = "hybrid"
            for rotation in (0, 90, 180, 270):
                rotated = cv2.cvtColor(
                    np.asarray(crop.rotate(-rotation, expand=True)), cv2.COLOR_RGB2BGR
                )
                items, warnings = read_text(rotated)
                report["orientation_smoke"].append(
                    {
                        "input_rotation_clockwise": rotation,
                        "exact_reading_found": any(
                            normalize(i["text"]).replace(" ", "") == "6Ω" for i in items
                        ),
                        "texts": items,
                        "warnings": warnings,
                    }
                )
            if args.real_count:
                from ..pipeline.engine import analyze_page
                from ..pipeline.preprocess import decode
                from ..pipeline.netlist import Netlist
                from .eval_e2e import graph
                import networkx as nx

                base = Path(load_config()["images"])
                paths = sorted(
                    p
                    for p in base.glob("*")
                    if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
                )[: args.real_count]
                for path in paths:
                    runs = {}
                    for backend in ("legacy", "hybrid"):
                        os.environ["CIRCUIT_OCR_BACKEND"] = backend
                        runs[backend] = analyze_page(decode(path.read_bytes()))
                    nets = [
                        Netlist.model_validate(runs[b]["netlist"]) for b in ("legacy", "hybrid")
                    ]
                    topology_same = nx.is_isomorphic(
                        graph(nets[0]),
                        graph(nets[1]),
                        node_match=lambda a, b: a["type"] == b["type"],
                    )
                    row = {
                        "image": path.name,
                        "topology_equal_between_backends": topology_same,
                        "independent_accuracy": None,
                        "runs": runs,
                    }
                    report["real_images"].append(row)
                    print(
                        json.dumps(
                            {
                                "image": path.name,
                                "topology_equal": topology_same,
                                "seconds": {b: runs[b]["timings"]["total"] for b in runs},
                            }
                        ),
                        flush=True,
                    )
            report["network_attempts"] = attempts
    finally:
        if previous is None:
            os.environ.pop("CIRCUIT_OCR_BACKEND", None)
        else:
            os.environ["CIRCUIT_OCR_BACKEND"] = previous
        dest = Path(args.out)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
