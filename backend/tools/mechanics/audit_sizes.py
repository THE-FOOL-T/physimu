"""Measure authored target sizes after aspect-preserving inference resize; no model scores."""

import argparse
from collections import defaultdict
import json
from pathlib import Path

import numpy as np
from PIL import Image

from .common import NAMES, contained, load_dataset, read_labels, sha256, write_json


def audit(root, imgsz=512):
    if imgsz < 32 or imgsz % 32:
        raise ValueError("Image size must be a positive multiple of 32")
    root = Path(root).resolve()
    manifest = load_dataset(root)
    sizes = defaultdict(list)
    splits = defaultdict(lambda: defaultdict(list))
    for row in manifest["records"]:
        with Image.open(root / row["image"]) as image:
            width, height = image.size
        scale = imgsz / max(width, height)
        for cls, (x0, y0, x1, y1) in read_labels(root / row["label"], width, height):
            size = min(x1 - x0, y1 - y0) * scale
            sizes[NAMES[cls]].append(size)
            splits[row["split"]][NAMES[cls]].append(size)

    def describe(values):
        return dict(
            instances=len(values),
            min_side_px_quantiles=dict(
                zip(("p10", "p50", "p90"), [float(v) for v in np.quantile(values, [0.1, 0.5, 0.9])])
            )
            if values
            else None,
            min_side_under_4_px=sum(v < 4 for v in values),
            min_side_under_8_px=sum(v < 8 for v in values),
        )

    return dict(
        kind="mechanics-target-size-audit",
        manifest_sha256=sha256(root / "manifest.json"),
        origin=manifest["origin"],
        images=len(manifest["records"]),
        imgsz=imgsz,
        resize="imgsz / max(native_width, native_height); box minimum side; padding has no effect",
        note="Geometric sizes only; thin targets are not automatically invalid. No recall, causality or real accuracy is inferred.",
        classes={name: describe(sizes[name]) for name in NAMES},
        splits={
            split: {name: describe(rows[name]) for name in NAMES} for split, rows in splits.items()
        },
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--imgsz", type=int, default=512)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    output = contained(args.out)
    if output.exists() or output.is_relative_to(args.dataset.resolve()):
        raise ValueError("Use a fresh report outside the dataset")
    result = audit(args.dataset, args.imgsz)
    output.parent.mkdir(parents=True, exist_ok=True)
    write_json(output, result)
    print(json.dumps(dict(images=result["images"], imgsz=args.imgsz, out=str(output))))


if __name__ == "__main__":
    main()
