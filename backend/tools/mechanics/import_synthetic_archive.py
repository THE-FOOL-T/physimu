"""Convert canonical synthetic annotations to the application's ordered detector taxonomy.

Archive metadata is used only for offline supervision, never for recognition.
Original test/OOD images remain held out. No archive code or README is executed.
"""

import argparse
from collections import Counter
import io
import json
from pathlib import Path, PurePosixPath
import shutil
import zipfile

from PIL import Image

from .common import NAMES, fresh, load_dataset, sha256, write_json, yolo_line


DIRECT = {
    "projectile": "ball",
    "block": "block",
    "pulley_wheel": "pulley",
    "pivot": "pivot",
    "pendulum_bob": "bob",
    "pendulum_string_or_rod": "rod",
    "rope": "rope",
    "dimension_line": "dimension_line",
    "angle_arc": "angle_mark",
    "trajectory_curve": "trajectory_arc",
    "equilibrium_line": "axis",
    "coordinate_axis": "axis",
    "text_region": "text_label",
}
SUBTYPES = {
    "inclined_plane": "incline_block",
    "pendulum": "pendulum",
    "projectile_motion": "projectile",
}


def canonical_boxes(scene):
    """Include strokes as well as objects; do not confuse a wedge with its contact edge."""
    geometry = scene["observed_geometry"]
    width, height = scene["width"], scene["height"]
    points = {p["name"]: (p["x"], p["y"]) for p in geometry["points"]}
    boxes = []
    ignored = Counter()
    for obj in geometry["objects"] + geometry["polylines"]:
        source = obj["class_name"]
        attrs = obj.get("attributes", {})
        role = attrs.get("attribute")
        name, box = DIRECT.get(source), obj["bbox"]
        if source == "support_surface":
            if role not in {"ceiling", "ground", "table", "platform"}:
                raise ValueError(f"Unknown support role: {role}")
            name = "ceiling" if role == "ceiling" else "floor"
        elif source == "wedge":
            edge = [points["wedge_apex"], points["wedge_incline_corner"]]
            box = [min(p[0] for p in edge) - 3, min(p[1] for p in edge) - 3,
                   max(p[0] for p in edge) + 3, max(p[1] for p in edge) + 3]
            name = "incline"
        elif source == "vector_arrow":
            if role not in {"initial_velocity", "weight", "normal", "friction", "tension", "gravity"}:
                raise ValueError(f"Unknown vector role: {role}")
            name = "arrow_velocity" if role == "initial_velocity" else "arrow_force"
        elif source in {"pulley_bracket", "motion_arrow"}:
            # A bracket isn't a second pulley; an acceleration arrow isn't velocity.
            ignored[source] += 1
            continue
        if name is None:
            raise ValueError(f"Unmapped annotation: {source}")
        clipped = [max(0, box[0]), max(0, box[1]), min(width, box[2]), min(height, box[3])]
        yolo_line(name, clipped, width, height)  # Reject nonfinite/empty/outside boxes.
        boxes.append((name, clipped))
    return boxes, ignored


def import_archive(archive, output, *, replay=None):
    archive = Path(archive).resolve(strict=True)
    out = fresh(output)
    (out / "images").mkdir()
    (out / "labels").mkdir()
    records, classes, ignored, original_splits = [], Counter(), Counter(), Counter()
    with zipfile.ZipFile(archive) as source:
        names = source.namelist()
        if len(set(names)) != len(names):
            raise ValueError("Duplicate archive paths")
        for name in names:
            path = PurePosixPath(name.replace("\\", "/"))
            if path.is_absolute() or ".." in path.parts or ":" in name:
                raise ValueError("Unsafe archive path")
        annotations = sorted(n for n in names if "/annotations/canonical/" in n and n.endswith(".json"))
        if not annotations:
            raise ValueError("No canonical synthetic annotations")
        for annotation in annotations:
            scene = json.loads(source.read(annotation))
            scene_id, split = scene["scene_id"], scene["split"]
            if PurePosixPath(scene_id).name != scene_id or split not in {"train", "val", "test", "ood"}:
                raise ValueError("Invalid scene identity/split")
            prefix = annotation.split("/annotations/canonical/")[0]
            payload = source.read(f"{prefix}/images/{split}/{scene_id}.png")
            with Image.open(io.BytesIO(payload)) as image:
                if image.size != (scene["width"], scene["height"]):
                    raise ValueError("Canonical image size mismatch")
                image.verify()
            boxes, skipped = canonical_boxes(scene)
            ignored.update(skipped)
            classes.update(name for name, _ in boxes)
            original_splits[split] += 1
            image_path = out / f"images/archive_{scene_id}.png"
            label_path = out / f"labels/archive_{scene_id}.txt"
            image_path.write_bytes(payload)
            label_path.write_text("\n".join(yolo_line(n, b, scene["width"], scene["height"]) for n, b in boxes) + "\n", encoding="utf-8")
            archetype = SUBTYPES.get(scene["subtype"])
            if scene["subtype"] == "pulley":
                configuration = scene["parameters"]["configuration"]
                if configuration not in {"atwood", "table_edge"}:
                    raise ValueError("Unknown pulley configuration")
                archetype = "atwood" if configuration == "atwood" else "table_pulley"
            records.append({
                "image": image_path.relative_to(out).as_posix(),
                "label": label_path.relative_to(out).as_posix(),
                "sha256": sha256(image_path), "label_sha256": sha256(label_path),
                "split": "pool" if split == "ood" else split,
                "original_split": split, "source_group": f"owner-archive-{scene_id}",
                "archetype": archetype, "style": "synthetic", "synthetic": True,
                "source": f"{archive.name}:{annotation}", "seed": scene["seed"],
            })
    # Replay missing families from the prior synthetic set to reduce catastrophic forgetting.
    # Their original split and provenance stay intact; no real evaluation image is included.
    if replay:
        replay = Path(replay).resolve(strict=True)
        manifest = load_dataset(replay)
        if manifest["origin"] != "synthetic":
            raise ValueError("Replay must be synthetic")
        present = {r["archetype"] for r in records}
        for index, row in enumerate(manifest["records"]):
            if row["archetype"] in present or row["split"] not in {"train", "val"}:
                continue
            image_path = out / f"images/replay_{index:04d}{Path(row['image']).suffix}"
            label_path = out / f"labels/replay_{index:04d}.txt"
            shutil.copyfile(replay / row["image"], image_path)
            shutil.copyfile(replay / row["label"], label_path)
            records.append({**row, "image": image_path.relative_to(out).as_posix(),
                            "label": label_path.relative_to(out).as_posix(), "synthetic": True,
                            "source": str(replay), "replay": True})
    manifest = {"domain": "mechanics", "origin": "synthetic", "class_names": list(NAMES),
                "archive_sha256": sha256(archive), "records": records,
                "conversion": {"original_splits": dict(original_splits), "archive_classes": dict(classes),
                               "ignored_annotations": dict(ignored), "ood_split": "pool",
                               "missing_families_replay": str(replay) if replay else None,
                               "real_images_used": 0}}
    write_json(out / "manifest.json", manifest)
    load_dataset(out)
    return {"dataset": str(out), "records": len(records),
            "splits": dict(Counter(r["split"] for r in records)), "conversion": manifest["conversion"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--replay", type=Path)
    args = parser.parse_args()
    print(json.dumps(import_archive(args.archive, args.out, replay=args.replay), indent=2))


if __name__ == "__main__":
    main()
