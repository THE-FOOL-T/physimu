"""Report frozen-test detector comparisons; smoke runs can never be promoted."""

import json
from pathlib import Path
from ..core.config import ROOT


def eligible(baseline, candidate):
    if "smoke" in candidate.get("split", "").lower():
        return False
    if baseline.get("count") != 99 or candidate.get("count") != 99:
        return False
    for name in ["resistor", "voltage_source"]:
        if (
            candidate["classes"].get(name, {}).get("recall_conf025", 0)
            < baseline["classes"][name]["recall_conf025"] - 0.02
        ):
            return False
    return all(
        candidate["classes"].get(name, {}).get("recall_conf025", 0)
        > baseline["classes"][name]["recall_conf025"]
        for name in ["capacitor", "switch", "ammeter", "voltmeter"]
    )


def main():
    files = {
        "v2": "reference_99_metrics.json",
        "fine_tune_smoke": "detector_smoke_finetune.json",
        "control_smoke": "detector_smoke_control.json",
    }
    results = {
        key: json.loads((ROOT / "docs" / filename).read_text(encoding="utf-8"))
        for key, filename in files.items()
    }
    report = "# Frozen detector test comparison\n\n99 reviewed images; confidence 0.25, matching IoU 0.5; AP uses IoU .50:.05:.95 and 101-point interpolation. Baseline inference size 640; smoke candidates use the same 640 protocol. Full fine-tuning is not completed: no CUDA GPU is available. These are 1-epoch plumbing runs on four training/two validation images, never a release candidate.\n\n|Model|Class|Precision|Recall|AP50|AP50–95|\n|---|---|---:|---:|---:|---:|\n"
    for name, result in results.items():
        for label, row in result["classes"].items():
            if not row["gold"]:
                continue
            report += (
                "|"
                + name
                + "|"
                + label
                + "|"
                + "|".join(
                    "null" if row[key] is None else f"{row[key]:.4f}"
                    for key in [
                        "precision_conf025",
                        "recall_conf025",
                        "AP50",
                        "AP50_95",
                    ]
                )
                + "|\n"
            )
    choice = eligible(results["v2"], results["fine_tune_smoke"])
    report += f"\nEligible for promotion: **{choice}**. Keep v2 selected. Full-model metrics and independent end-to-end accuracy remain **null**. Raw confusion matrices: `reference_99_metrics.json`, `detector_smoke_finetune.json`, `detector_smoke_control.json`; corresponding PNGs show their matrices.\n"
    report += "\n## Reproduce full preparation/training\n\n1. Install dependencies; place v2 and the standard pretrained control in models. See dataset_sources.md for license/export restrictions.\n2. Import original owner training material and licensed public exports; review maps, completeness and all pseudo-labels. Record per-image real/synthetic provenance in kinds.json.\n3. `python -m backend.tools.merge_dataset data/raw/owner-training data/raw/aitee/remapped data/generated_round2_oriented --original-training /path/to/original/images/train --out data/merged/reviewed --eval /path/to/frozen99/images --quarantine-frozen`\n4. After actual human completeness review, record it in manifest.json.\n5. GPU command: `python -m backend.tools.train --data data/merged/reviewed/data.yaml --control models/yolo26n.pt --device 0 --epochs 50 --imgsz 960 --seed 42 --execute`. Add `--resume /absolute/path/to/last.pt` to resume one run.\n6. Evaluate both checkpoints with eval_detector at the same input size, frozen images/labels/names, then compare the rare-class improvement and two-point resistor/source rule. Do not select on training fit.\n\nGPU duration: **null**, unmeasured on this host. Estimate it on the owner GPU with `--smoke --execute` first; scale measured epoch time by training batches × epochs, allowing validation overhead. No multi-hour CPU training was run.\n"
    (ROOT / "docs/detector_results.md").write_text(report, encoding="utf-8")
    (ROOT / "docs/detector_selection.json").write_text(
        json.dumps(
            {
                "eligible": choice,
                "selected": "v2",
                "full_finetune_metrics": None,
                "full_control_metrics": None,
                "reason": "Smoke-only candidates; full training and independent real data still required",
            },
            indent=2,
        )
    )
    print("Wrote honest smoke comparison; v2 remains selected")


if __name__ == "__main__":
    main()
