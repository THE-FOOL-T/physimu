"""Assignment coverage is measured separately from reviewed text accuracy."""

import argparse
import json
from pathlib import Path

from ..core.config import load_config
from ..domains.circuit.engine import analyze_page
from ..core.preprocess import decode
from .ocr_debug import ROOT, annotate, debug_report


def assignment_rate(results):
    parts = [c for result in results for c in result["netlist"]["components"]]
    given = sum(c["value"]["status"] == "given" for c in parts)
    return {
        "given": given,
        "components": len(parts),
        "rate": given / len(parts) if parts else None,
    }


def gold_score(reports, gold_files):
    gold = [json.loads(path.read_text(encoding="utf-8")) for path in gold_files]
    gold = [entry for entry in gold if entry.get("human_reviewed") is True]
    if not gold:
        return {
            "reviewed_images": 0,
            "text_accuracy": None,
            "assignment_accuracy": None,
        }
    from ..domains.circuit.values import normalize
    from scipy.optimize import linear_sum_assignment
    import numpy as np
    from ..core.ocr_regions import intersection, area

    found = correct = assigned = matched_images = 0
    for entry in gold:
        report = next((r for r in reports if r["sha256"] == entry.get("sha256")), None)
        if not report:
            continue
        matched_images += 1
        expected = entry["texts"]
        items = report["diagnostics"].get("texts", [])
        found += len(expected)
        if not expected or not items:
            continue
        overlaps = np.zeros((len(expected), len(items)))
        for row, label in enumerate(expected):
            for column, item in enumerate(items):
                shared = intersection(label["bbox"], item["bbox"])
                overlaps[row, column] = shared / max(
                    1, area(label["bbox"]) + area(item["bbox"]) - shared
                )
        rows, columns = linear_sum_assignment(1 - overlaps)
        for row, column in zip(rows, columns):
            if overlaps[row, column] < 0.5:
                continue
            label = expected[row]
            item = items[column]
            exact = normalize(item["text"]).replace(" ", "") == normalize(label["text"]).replace(
                " ", ""
            )
            correct += exact
            assigned += bool(exact and item.get("assigned_to") == label.get("component_id"))
    return {
        "reviewed_images": matched_images,
        "text_accuracy": correct / found if found else None,
        "assignment_accuracy": assigned / found if found else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--images")
    parser.add_argument("--baseline")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--out", default="docs/ocr_assignment_round3.json")
    args = parser.parse_args()
    base = Path(args.images or load_config()["images"])
    paths = sorted(
        p for p in base.rglob("*") if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    )
    before = []
    if args.baseline:
        before = [
            json.loads(line)
            for line in Path(args.baseline).read_text(encoding="utf-8").splitlines()
        ]
        before = sorted(
            (r for r in before if "result" in r),
            key=lambda r: (-r.get("assumed", 0), r.get("index", 0)),
        )[: args.limit]
        selected = {r["image"] for r in before}
        paths = [p for p in paths if p.name in selected]
    else:
        paths = paths[: args.limit]
    results = []
    reports = []
    cache = ROOT / ".cache/round3"
    cache.mkdir(parents=True, exist_ok=True)
    with (cache / "after.jsonl").open("w", encoding="utf-8") as stream:
        for index, path in enumerate(paths):
            result = analyze_page(decode(path.read_bytes()))
            results.append(result)
            report = debug_report(path, result)
            reports.append(report)
            stream.write(
                json.dumps({"image": path.name, "result": result}, ensure_ascii=False) + "\n"
            )
            stream.flush()
            annotate(result, cache / (f"case-{index + 1:03}.png"))
            print(
                json.dumps({"image": path.name, **assignment_rate([result])}),
                flush=True,
            )
    summary = {
        "scope": "Fraction of detected components marked given; coverage, not correctness.",
        "images": [r["image"] for r in reports],
        "before": assignment_rate([r["result"] for r in before]) if before else None,
        "after": assignment_rate(results),
        "gold": gold_score(reports, list((ROOT / "data/eval/text_gold").glob("*.json"))),
        "reports": reports,
    }
    out = Path(args.out).resolve()
    if not out.is_relative_to(ROOT):
        parser.error("Output must stay in this repository")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "reports"}))


if __name__ == "__main__":
    main()
