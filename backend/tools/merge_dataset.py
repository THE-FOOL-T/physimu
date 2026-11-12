"""Merge reviewed, license-documented YOLO datasets with content-based split isolation."""

import argparse
import hashlib
import json
from pathlib import Path
import random
import shutil
import yaml
from .leakage import check_frozen, balanced_records, duplicate_groups
from ..config import load_config

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def images(path):
    return [
        p for p in Path(path).rglob("*") if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    ]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("datasets", nargs="+")
    p.add_argument("--original-training", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--eval", default=load_config()["additional_images"])
    p.add_argument("--quarantine-frozen", action="store_true")
    args = p.parse_args()
    dest = Path(args.out)
    if dest.exists() and any(dest.iterdir()):
        p.error("Output must be new or empty")
    frozen = images(args.eval)
    if not frozen:
        p.error("Frozen test images are required; pass --eval or CIRCUIT_EXTRA_IMAGES")
    frozen_manifest = ROOT / "data/eval/frozen99.json"
    if frozen_manifest.is_file():
        published = json.loads(frozen_manifest.read_text(encoding="utf-8"))
        if {row["sha256"] for row in published["images"]} != {digest(path) for path in frozen}:
            p.error("Frozen test image hashes changed; refusing training preparation")
    forbidden = {digest(i) for i in frozen}
    rows = {}
    origins = {}
    for directory in args.datasets:
        base = Path(directory)
        if not (base / "SOURCE.md").is_file():
            p.error(f"Missing SOURCE.md license record: {base}")
        kinds = (
            json.loads((base / "kinds.json").read_text(encoding="utf-8"))
            if (base / "kinds.json").is_file()
            else {}
        )
        for im in images(base / "images"):
            d = digest(im)
            label = base / "labels" / (im.stem + ".txt")
            if d in forbidden:
                p.error(f"Frozen eval leakage: {im}")
            if not label.exists():
                p.error(f"Missing reviewed labels: {im}")
            if (
                d in rows
                and rows[d][1].read_text(encoding="utf-8").strip()
                != label.read_text(encoding="utf-8").strip()
            ):
                p.error(f"Conflicting duplicate labels: {im}")
            rows[d] = (im, label)
            kind = kinds.get(im.name, "synthetic_or_unknown")
            origins[d] = {
                "synthetic": kind != "real",
                "provenance_kind": kind,
                "dataset": str(base),
            }
    collisions = check_frozen([row[0] for row in rows.values()], frozen)
    if collisions:
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "leakage.json").write_text(json.dumps(collisions, indent=2))
        if not args.quarantine_frozen:
            p.error(
                "Near-duplicate frozen-test candidates found. Review leakage.json; no training data written."
            )
        excluded = {str(c["training"]) for c in collisions}
        rows = {d: row for d, row in rows.items() if str(row[0]) not in excluded}
    original = {digest(i) for i in images(args.original_training)}
    excluded_hashes = (
        {digest(c["training"]) for c in collisions} if args.quarantine_frozen else set()
    )
    if not (original - excluded_hashes).issubset(rows):
        p.error(f"Merged data is missing original training images outside frozen-test quarantine")
    manifest = []
    keys = sorted(rows)
    groups = duplicate_groups([rows[d][0] for d in keys])
    group_ids = sorted(set(groups.values()))
    random.Random(42).shuffle(group_ids)
    validation = set(group_ids[: max(1, len(group_ids) // 5)])
    for i, d in enumerate(keys):
        im, label = rows[d]
        split = "val" if groups[str(im)] in validation else "train"
        name = d[:20]
        for folder in ["images", "labels"]:
            (dest / folder / split).mkdir(parents=True, exist_ok=True)
        shutil.copy2(im, dest / "images" / split / (name + im.suffix.lower()))
        shutil.copy2(label, dest / "labels" / split / (name + ".txt"))
        manifest.append(
            {
                "sha256": d,
                "source": str(im),
                "split": split,
                "duplicate_group": groups[str(im)],
                "original_training": d in original,
                **origins[d],
                "image": str((dest / "images" / split / (name + im.suffix.lower())).resolve()),
            }
        )
    training = balanced_records([r for r in manifest if r["split"] == "train"])
    (dest / "train.txt").write_text("\n".join(r["image"] for r in training) + "\n")
    names = yaml.safe_load((ROOT / "data/class_schema.yaml").read_text(encoding="utf-8"))["names"]
    (dest / "data.yaml").write_text(
        yaml.safe_dump(
            {
                "path": str(dest.resolve()),
                "train": "train.txt",
                "val": "images/val",
                "names": names,
            }
        )
    )
    (dest / "manifest.json").write_text(
        json.dumps(
            {
                "original_training_count": len(original - excluded_hashes),
                "quarantined_original_count": len(original & excluded_hashes),
                "frozen_test_count": len(frozen),
                "near_duplicate_check": True,
                "synthetic_training_fraction": sum(r["synthetic"] for r in training)
                / len(training),
                "records": manifest,
            },
            indent=2,
        )
    )
    print(
        f"Merged {len(keys)} images; original training, near-duplicate isolation and synthetic cap checked"
    )


if __name__ == "__main__":
    main()
