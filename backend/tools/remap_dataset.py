"""Normalize YOLO, COCO, or VOC annotations via an explicit owner-approved map."""

import argparse
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET
import yaml
from PIL import Image


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--format", choices=["yolo", "coco", "voc"], required=True)
    p.add_argument("--images", required=True)
    p.add_argument("--annotations", required=True)
    p.add_argument("--map", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    cfg = yaml.safe_load(Path(args.map).read_text(encoding="utf-8"))
    mapping = {str(k): v for k, v in cfg["map"].items()}
    names = cfg["names"]
    dest = Path(args.out)
    if not (
        cfg.get("license_verified_by_owner")
        or cfg.get("license_verified")
        and cfg.get("license_url")
    ):
        p.error("Record a verified license and its primary-source URL in the map YAML first")
    if not Path(args.images).is_dir() or not Path(args.annotations).exists():
        p.error("Dataset assets are absent; obtain the licensed export first")
    if dest.exists() and any(dest.iterdir()):
        p.error("Output must be new or empty")
    (dest / "images").mkdir(parents=True)
    (dest / "labels").mkdir()
    rows = {}
    dropped = {}
    paths = {
        p.name: p
        for p in Path(args.images).rglob("*")
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    }

    def add(filename, cls, box):
        key = str(cls)
        target = mapping.get(key)
        if target is None:
            dropped[key] = dropped.get(key, 0) + 1
            return
        if isinstance(target, str):
            target = names.index(target)
        rows.setdefault(filename, []).append((int(target), box))

    if args.format == "coco":
        data = json.loads(Path(args.annotations).read_text(encoding="utf-8"))
        images = {i["id"]: i for i in data["images"]}
        categories = {i["id"]: i["name"] for i in data["categories"]}
        for a in data["annotations"]:
            im = images[a["image_id"]]
            x, y, w, h = a["bbox"]
            add(
                Path(im["file_name"]).name,
                categories[a["category_id"]],
                [
                    (x + w / 2) / im["width"],
                    (y + h / 2) / im["height"],
                    w / im["width"],
                    h / im["height"],
                ],
            )
    elif args.format == "voc":
        for path in Path(args.annotations).rglob("*.xml"):
            root = ET.parse(path).getroot()
            filename = Path(root.findtext("filename")).name
            w = float(root.findtext("size/width"))
            h = float(root.findtext("size/height"))
            for obj in root.findall("object"):
                b = obj.find("bndbox")
                x1, y1, x2, y2 = [float(b.findtext(k)) for k in ["xmin", "ymin", "xmax", "ymax"]]
                add(
                    filename,
                    obj.findtext("name"),
                    [
                        (x1 + x2) / 2 / w,
                        (y1 + y2) / 2 / h,
                        (x2 - x1) / w,
                        (y2 - y1) / h,
                    ],
                )
    else:
        for filename, path in paths.items():
            label = Path(args.annotations) / (path.stem + ".txt")
            if label.exists():
                for line in label.read_text(encoding="utf-8").splitlines():
                    cls, *box = line.split()
                    add(filename, cls, list(map(float, box[:4])))
    for filename, path in paths.items():
        shutil.copy2(path, dest / "images" / filename)
        (dest / "labels" / (path.stem + ".txt")).write_text(
            "\n".join(
                str(cls) + " " + " ".join(f"{v:.8f}" for v in box)
                for cls, box in rows.get(filename, [])
            )
        )
    (dest / "data.yaml").write_text(
        yaml.safe_dump(
            {
                "path": str(dest.resolve()),
                "train": "images",
                "val": "images",
                "names": names,
            },
            allow_unicode=True,
        )
    )
    (dest / "SOURCE.md").write_text(
        f"Source: {cfg.get('source', 'unspecified')}\n\nLicense: {cfg.get('license', 'unspecified')}\n\nLicense evidence: {cfg.get('license_url', 'owner record')}\n\nOwner verified: {bool(cfg.get('license_verified_by_owner'))}\n",
        encoding="utf-8",
    )
    (dest / "audit.json").write_text(
        json.dumps(
            {
                "images": len(paths),
                "dropped_classes": dropped,
                "potential_unlabeled_objects": list(paths),
                "reason": "A remap cannot establish label completeness. All images require review for schema classes absent from the source taxonomy.",
            },
            indent=2,
        )
    )
    print(f"Converted {len(paths)} images; review audit.json before merging or training")


if __name__ == "__main__":
    main()
