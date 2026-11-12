"""Evaluate OCR-to-component association against owner-annotated JSONL records.

Each JSONL row contains:
  {"components": [Component JSON, ...],
   "texts": [{"text": "...", "bbox": [x1,y1,x2,y2],
              "confidence": 0.95, "target_component": "R1"}, ...]}

The target_component field is ground truth and is ignored by associate().
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from collections import Counter

from ..pipeline.associate import associate
from ..pipeline.netlist import Component


def evaluate(path: Path):
    total = assigned = correct = wrong = 0
    reasons = Counter()
    records = 0

    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            records += 1
            components = [Component.model_validate(item) for item in row["components"]]
            texts = [dict(item) for item in row["texts"]]
            component_ids = {component.id for component in components}
            for item in texts:
                target = item.get("target_component")
                if target is not None and target not in component_ids:
                    raise ValueError(
                        f"Ground-truth component {target!r} is absent from record {records}."
                    )

            result = associate(components, texts)

            unmatched_by_text = {item["text"]: item["reason"] for item in result["unmatched"]}
            for item in texts:
                target = item.get("target_component")
                if target is None:
                    continue
                total += 1
                link = item.get("association")
                if link is None:
                    reasons[unmatched_by_text.get(item["text"], "unmatched")] += 1
                    continue
                assigned += 1
                if link["component_id"] == target:
                    correct += 1
                else:
                    wrong += 1

    if total == 0:
        raise ValueError("No text records with target_component ground truth were found.")

    precision = correct / assigned if assigned else 0.0
    coverage = assigned / total
    recall = correct / total
    return {
        "records": records,
        "annotated_text_regions": total,
        "assigned_text_regions": assigned,
        "correct_assignments": correct,
        "wrong_assignments": wrong,
        "unassigned_text_regions": total - assigned,
        "precision_when_assigned": round(precision, 4),
        "assignment_coverage": round(coverage, 4),
        "correct_over_all_annotated": round(recall, 4),
        "meets_90_percent_precision_and_coverage": precision >= 0.90 and coverage >= 0.90,
        "unassigned_reasons": dict(reasons),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Annotated JSONL file")
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    args = parser.parse_args()

    report = evaluate(args.input)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
