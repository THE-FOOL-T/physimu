"""Import reviewed YOLO exports only with per-image HUMAN attestations and provenance."""

import argparse
from datetime import date
import json
from pathlib import Path
import shutil

from PIL import Image
import yaml

from .common import (
    ARCHETYPES,
    NAMES,
    fresh,
    images,
    relative_file,
    read_labels,
    sha256,
    write_json,
    yolo_line,
    contained,
)
from .leakage import audit


def import_export(folder, review_file, output, *, class_map=None, frozen_root=None):
    folder = Path(folder).resolve()
    if contained(output).is_relative_to(folder):
        raise ValueError("Reviewed imports must not write into the source export")
    review_file = Path(review_file).resolve()
    review = json.loads(review_file.read_text(encoding="utf-8"))
    if review.get("kind") != "mechanics-human-review" or review.get("version") != 1:
        raise ValueError("Explicit HUMAN review manifest is required")
    names = review.get("class_names")
    if not isinstance(names, list) or not names or len(set(names)) != len(names):
        raise ValueError("Export class order is required")
    mapping = (
        class_map if class_map is not None else {name: name for name in names if name in NAMES}
    )
    if set(mapping) != set(names) or any(
        target is not None and target not in NAMES for target in mapping.values()
    ):
        raise ValueError(
            "Map every source class explicitly; use null to drop unmapped classes, never guess"
        )
    records = review.get("records", [])
    if not records:
        raise ValueError("No reviewed records")
    checked = []
    seen = set()
    for row in records:
        if row.get("human_reviewed") is not True or any(
            not str(row.get(k, "")).strip()
            for k in ("reviewer", "source_group", "source", "licence_note")
        ):
            raise ValueError("Every image needs HUMAN review and source/licence notes")
        date.fromisoformat(row["reviewed_at"])
        if (
            row.get("archetype") not in ARCHETYPES
            or row.get("style") not in {"printed", "handwritten", "photo"}
            or row.get("split") not in {"train", "val", "pool"}
        ):
            raise ValueError("Invalid reviewed archetype/style/split")
        image = relative_file(folder, row["image"])
        label = relative_file(folder, row["label"])
        if (
            image in seen
            or sha256(image) != row.get("sha256")
            or sha256(label) != row.get("reviewed_label_sha256")
        ):
            raise ValueError("Duplicate image or reviewed image/label hash mismatch")
        seen.add(image)
        with Image.open(image) as raster:
            w, h = raster.size
        labels = read_labels(label, w, h, names)
        lines = [
            yolo_line(mapping[names[cls]], box, w, h)
            for cls, box in labels
            if mapping[names[cls]] is not None
        ]
        checked.append((row, image, lines, len(labels) - len(lines)))
    if set(images(folder / "images")) != seen:
        raise ValueError("Every exported image must be explicitly reviewed")
    out = fresh(output)
    (out / "images").mkdir()
    (out / "labels").mkdir()
    imported = []
    for i, (row, image, lines, dropped) in enumerate(checked):
        name = f"real_{i:04d}{image.suffix.lower()}"
        label = f"real_{i:04d}.txt"
        shutil.copyfile(image, out / "images" / name)
        (out / "labels" / label).write_text(
            "\n".join(lines) + ("\n" if lines else ""), encoding="utf-8"
        )
        imported.append(
            {
                **row,
                "image": f"images/{name}",
                "label": f"labels/{label}",
                "label_sha256": sha256(out / "labels" / label),
                "synthetic": False,
                "dropped_unmapped_classes": dropped,
                "review_manifest_sha256": sha256(review_file),
            }
        )
    manifest = {
        "version": 1,
        "domain": "mechanics",
        "origin": "real",
        "class_names": list(NAMES),
        "source_class_map": mapping,
        "records": imported,
    }
    leakage = audit(manifest, out, **({"frozen_root": frozen_root} if frozen_root else {}))
    write_json(out / "leakage.json", leakage)
    if not leakage["passed"]:
        write_json(
            out / "REJECTED.json",
            {"reason": "Frozen/source/near-duplicate leakage; no trainable manifest was created."},
        )
        raise ValueError("Reviewed export failed leakage audit")
    write_json(out / "manifest.json", manifest)
    for split in ("train", "val", "pool"):
        (out / (split + ".txt")).write_text(
            "\n".join("./" + r["image"] for r in imported if r["split"] == split) + "\n",
            encoding="utf-8",
        )
    (out / "data.yaml").write_text(
        yaml.safe_dump(
            {"path": str(out), "train": "train.txt", "val": "val.txt", "names": list(NAMES)}
        ),
        encoding="utf-8",
    )
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("export", type=Path)
    p.add_argument("--review", required=True, type=Path)
    p.add_argument("--class-map", type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    mapping = yaml.safe_load(a.class_map.read_text(encoding="utf-8")) if a.class_map else None
    result = import_export(a.export, a.review, a.out, class_map=mapping)
    print(
        f"Imported {len(result['records'])} HUMAN-reviewed images; source/licence notes are owner attestations."
    )


if __name__ == "__main__":
    main()
