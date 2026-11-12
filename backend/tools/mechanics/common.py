"""Mechanics-only data contracts and contained, non-destructive output helpers."""

import hashlib
import json
import math
from pathlib import Path

import yaml
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
FROZEN = ROOT / "data/eval/mechanics"
ARCHETYPES = (
    "projectile",
    "incline_block",
    "pendulum",
    "spring_mass",
    "atwood",
    "table_pulley",
    "incline_pulley",
    "collision_1d",
)
NAMES = tuple(
    yaml.safe_load((ROOT / "data/mechanics_class_schema.yaml").read_text(encoding="utf-8"))["names"]
)
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def images(folder):
    return sorted(
        p for p in Path(folder).rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES
    )


def contained(path, *, allow_frozen=False):
    raw = Path(path)
    if not raw.is_absolute():
        raise ValueError("Output paths must be explicitly absolute")
    result = raw.resolve()
    if result == ROOT or not result.is_relative_to(ROOT):
        raise ValueError("Output must stay inside this workspace")
    if not allow_frozen and (result == FROZEN or result.is_relative_to(FROZEN)):
        raise ValueError("Tools never write frozen gold scenes")
    return result


def fresh(path):
    result = contained(path)
    if result.exists() and (not result.is_dir() or any(result.iterdir())):
        raise ValueError("Output directory must be new or empty")
    result.mkdir(parents=True, exist_ok=True)
    return result


def write_json(path, obj):
    path = Path(path)
    path.write_text(
        json.dumps(obj, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8"
    )


def relative_file(root, name):
    root = Path(root).resolve()
    if not isinstance(name, str) or Path(name).is_absolute():
        raise ValueError("Manifest paths must be relative")
    path = (root / name).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError(f"Missing/escaping manifest file: {name}")
    return path


def read_labels(path, width, height, names=NAMES):
    rows = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        fields = line.split()
        if len(fields) != 5:
            raise ValueError("YOLO boxes need exactly class cx cy w h")
        cls, x, y, w, h = map(float, fields)
        if (
            not all(math.isfinite(v) for v in (cls, x, y, w, h))
            or not cls.is_integer()
            or not 0 <= cls < len(names)
        ):
            raise ValueError("Invalid class or nonfinite YOLO coordinate")
        if not (
            w > 0
            and h > 0
            and x - w / 2 >= -1e-8
            and y - h / 2 >= -1e-8
            and x + w / 2 <= 1 + 1e-8
            and y + h / 2 <= 1 + 1e-8
        ):
            raise ValueError("YOLO box leaves image")
        rows.append(
            (
                int(cls),
                [
                    (x - w / 2) * width,
                    (y - h / 2) * height,
                    (x + w / 2) * width,
                    (y + h / 2) * height,
                ],
            )
        )
    return rows


def yolo_line(name, box, width, height):
    x0, y0, x1, y1 = box
    if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
        raise ValueError(f"Invalid {name} box: {box}")
    return f"{NAMES.index(name)} {(x0 + x1) / 2 / width:.9f} {(y0 + y1) / 2 / height:.9f} {(x1 - x0) / width:.9f} {(y1 - y0) / height:.9f}"


def load_dataset(root, *, reviewed_real=True):
    root = Path(root).resolve()
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("domain") != "mechanics" or manifest.get("class_names") != list(NAMES):
        raise ValueError("Mechanics class order/manifest mismatch")
    if manifest.get("origin") not in {"synthetic", "real"}:
        raise ValueError("Explicit synthetic/real origin is required")
    records = manifest.get("records", [])
    seen = set()
    for row in records:
        image = relative_file(root, row["image"])
        if str(image) in seen:
            raise ValueError("Duplicate manifest image")
        seen.add(str(image))
        if row.get("sha256") != sha256(image) or row.get("split") not in {
            "train",
            "val",
            "test",
            "pool",
        }:
            raise ValueError("Image hash/split mismatch")
        if not row.get("source_group") or row.get("archetype") not in ARCHETYPES:
            raise ValueError("Source group and supported archetype are required")
        if (
            manifest["origin"] == "real"
            and reviewed_real
            and (
                row.get("human_reviewed") is not True
                or not row.get("reviewer")
                or not row.get("source")
                or not row.get("licence_note")
            )
        ):
            raise ValueError("Real data needs per-image human review and source/licence notes")
        label = relative_file(root, row["label"])
        if row.get("label_sha256") != sha256(label):
            raise ValueError("Label hash mismatch")
        with Image.open(image) as raster:
            read_labels(label, *raster.size)
    if set(images(root / "images")) != {relative_file(root, row["image"]) for row in records}:
        raise ValueError("Unrecorded/missing dataset images")
    return manifest
