"""Read/validate HUMAN gold; record immutable hashes without writing any scene."""

import argparse
from datetime import date
import json
from pathlib import Path

from PIL import Image

from ...domains.mechanics.scene import Scene
from .common import FROZEN, contained, relative_file, sha256, read_labels


def validate_gold(path):
    path = Path(path).resolve(strict=True)
    item = json.loads(path.read_text(encoding="utf-8"))
    if (
        set(item) != {"kind", "version", "source", "review", "scene"}
        or item["kind"] != "mechanics-human-gold"
        or item["version"] != 1
    ):
        raise ValueError("Invalid human gold envelope")
    review, source = item["review"], item["source"]
    if review.get("human_reviewed") is not True or not str(review.get("reviewer", "")).strip():
        raise ValueError("HUMAN review is required; proposals/templates are not gold")
    date.fromisoformat(review["reviewed_at"])
    if (
        any(not str(source.get(key, "")).strip() for key in ("group", "reference", "licence_note"))
        or "HUMAN decision required" in source["licence_note"]
    ):
        raise ValueError("HUMAN source/group/licence decisions are required")
    image = relative_file(path.parent, source["image"])
    if sha256(image) != source["sha256"]:
        raise ValueError("Gold source hash changed")
    scene = Scene.model_validate(item["scene"])
    if scene.meta.provenance != "authored" or scene.meta.style not in {"printed", "handwritten"}:
        raise ValueError("Gold must identify manual authorship and printed/handwritten style")
    with Image.open(image) as raster:
        if raster.size != (scene.image.width, scene.image.height):
            raise ValueError("Gold scene and actual image dimensions differ")
    result = {
        "gold": str(path),
        "image": str(image),
        "sha256": sha256(image),
        "scene_sha256": sha256(path),
        "source_group": source["group"],
        "style": scene.meta.style,
        "archetype": scene.archetype,
        "reviewer": review["reviewer"],
    }
    if source.get("labels"):
        labels = relative_file(path.parent, source["labels"])
        if sha256(labels) != source.get("labels_sha256"):
            raise ValueError("Reviewed detector-label hash changed")
        read_labels(labels, scene.image.width, scene.image.height)
        result.update(labels=str(labels), labels_sha256=sha256(labels))
    return result


def inventory(root=FROZEN):
    root = Path(root).resolve()
    rows = []
    for style in ("printed", "handwritten"):
        for path in sorted((root / style).rglob("*.gold.json")):
            row = validate_gold(path)
            if row["style"] != style:
                raise ValueError("Gold style disagrees with its partition")
            rows.append(row)
    seen = set()
    for row in rows:
        if row["sha256"] in seen:
            raise ValueError("Duplicate frozen source image")
        seen.add(row["sha256"])
    return rows


def portable_records(rows, root):
    return [
        {
            **r,
            **{
                key: Path(r[key]).relative_to(root).as_posix()
                for key in ("gold", "image", "labels")
                if key in r
            },
        }
        for r in rows
    ]


def freeze(root, output):
    root = Path(root).resolve()
    rows = inventory(root)
    if not rows:
        raise ValueError("No HUMAN gold exists; cannot claim a frozen set")
    out = contained(output, allow_frozen=True)
    if out.is_relative_to(FROZEN) and out != FROZEN / "frozen.json":
        raise ValueError("Only hash metadata, never scenes, may be written in frozen folders")
    out.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "kind": "mechanics-frozen-hash-manifest",
        "version": 1,
        "root": ".",
        "records": portable_records(rows, root),
        "counts": {
            style: sum(r["style"] == style for r in rows) for style in ("printed", "handwritten")
        },
        "minimum_20_each_met": all(
            sum(r["style"] == style for r in rows) >= 20 for style in ("printed", "handwritten")
        ),
    }
    with out.open("x", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    return result


def verify_frozen(root=FROZEN):
    root = Path(root).resolve()
    rows = inventory(root)
    manifest = root / "frozen.json"
    if rows and not manifest.is_file():
        raise ValueError("HUMAN gold exists but its freeze-hash manifest is missing")
    if manifest.is_file():
        frozen = json.loads(manifest.read_text(encoding="utf-8"))
        if frozen.get("kind") != "mechanics-frozen-hash-manifest" or frozen[
            "records"
        ] != portable_records(rows, root):
            raise ValueError("Frozen source/scene/group hashes changed")
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=FROZEN)
    p.add_argument("--scene", type=Path)
    p.add_argument("--freeze-out", type=Path)
    args = p.parse_args()
    result = (
        validate_gold(args.scene)
        if args.scene
        else (
            freeze(args.root, args.freeze_out)
            if args.freeze_out
            else {
                "records": verify_frozen(args.root),
                "human_task": "Supply 20 printed and 20 handwritten independently reviewed gold scenes.",
            }
        )
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
