"""Reproducible per-class counts; absent classes are zero, absent data are null."""

import collections
import json
from pathlib import Path
import yaml
from ..core.config import load_config, ROOT


def count(labels, names):
    result = collections.Counter()
    paths = list(Path(labels).glob("*.txt"))
    if not paths:
        return None
    for path in paths:
        for row in path.read_text(encoding="utf-8").splitlines():
            if row.strip():
                result[names[int(row.split()[0])]] += 1
    return dict(result)


def main():
    cfg = load_config()
    names = yaml.safe_load((ROOT / "data/class_schema.yaml").read_text(encoding="utf-8"))["names"]
    seen = json.loads((ROOT / "docs/baseline_v2.json").read_text(encoding="utf-8"))
    reference = json.loads((ROOT / "docs/reference_99_metrics.json").read_text(encoding="utf-8"))
    synthetic = count(ROOT / "data/generated_round2_oriented/labels", names)
    public = count(ROOT / "data/raw/aitee/remapped/labels", names)
    result = {
        "seen_images": seen["count"],
        "frozen_images": reference["count"],
        "synthetic_images": len(
            list((ROOT / "data/generated_round2_oriented/labels").glob("*.txt"))
        ),
        "aitee_images": len(list((ROOT / "data/raw/aitee/remapped/labels").glob("*.txt"))),
        "classes": {},
    }
    for name in names:
        result["classes"][name] = {
            "seen59": seen["classes"].get(name, {}).get("gold", 0),
            "frozen99": reference["classes"].get(name, {}).get("gold", 0),
            "synthetic": None if synthetic is None else synthetic.get(name, 0),
            "aitee": None if public is None else public.get(name, 0),
        }
    (ROOT / "docs/data_inventory.json").write_text(json.dumps(result, indent=2))
    report = "# Detector data inventory\n\nSeen 59 and frozen 99 counts reuse their recorded reviewed annotation audits. Generated and AITEE counts are read from local labels by this script.\n\n|Class|Seen 59|Frozen 99|Synthetic 24|AITEE 828|\n|---|---:|---:|---:|---:|\n"
    for name, row in result["classes"].items():
        report += (
            "|"
            + name
            + "|"
            + "|".join(str(row[k]) for k in ["seen59", "frozen99", "synthetic", "aitee"])
            + "|\n"
        )
    report += "\nAll rare classes remain starved of reviewed real data, especially capacitor, switch and all meters. Synthetic coverage is not evidence of real recall. The frozen 99 test images never enter training or validation. AITEE ambiguous P/V classes are dropped pending taxonomy review; pseudo-label additions are unreviewed and excluded from training.\n\nRun: `python -m backend.tools.data_inventory`. Licenses/access and maps: `dataset_sources.md`.\n"
    (ROOT / "docs/data_inventory.md").write_text(report, encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "classes"}))


if __name__ == "__main__":
    main()
