"""Seeded R1 mechanics images/labels/scenes/masks. Synthetic, never real accuracy."""

import argparse
from collections import Counter
import json
import math
from pathlib import Path
import random

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import yaml

from ...core import duplicate_groups
from ...domains.mechanics.scene import Scene
from .build_fixtures import fixtures, value
from .common import ARCHETYPES, NAMES, fresh, sha256, write_json, yolo_line
from .synthetic_painter import render, texture
from .handwriting import elastic_parameters, deform, inverse_maps, warp, notebook

STYLES = ("printed", "scan", "handwritten", "photo")


def schedules(count, seed):
    if count < 8:
        raise ValueError("Need at least eight examples for archetype coverage")
    rng = random.Random(seed)
    archetypes = [ARCHETYPES[i % len(ARCHETYPES)] for i in range(count)]
    counts = [round(count * f) for f in (0.3, 0.2, 0.3)]
    counts.append(count - sum(counts))
    styles = [style for style, n in zip(STYLES, counts) for _ in range(n)]
    mirrored = [i < round(count * 0.5) for i in range(count)]
    no_values = [i < round(count * 0.25) for i in range(count)]
    bengali = [i < round(count * 0.1) for i in range(count)]
    for a in (archetypes, styles, mirrored, no_values, bengali):
        rng.shuffle(a)
    return list(zip(archetypes, styles, mirrored, no_values, bengali))


def label(scene, id, text, x, y, bound_to=None):
    scene["annotations"].append(
        {
            "id": id,
            "type": "label",
            "geometry": {"text": text, "bbox": [x, y, x + max(20, len(text) * 14), y + 30]},
            "bound_to": bound_to,
        }
    )


def variant(source, rng, no_values, bengali):
    s = source.model_dump(mode="json", by_alias=True)
    s["image"].update(width=920, height=620)
    s["annotations"] = [
        a for a in s["annotations"] if a["type"] != "label" or a["id"].startswith("label_")
    ]
    for b in s["bindings"]:
        b["labels"] = []
    for body in s["bodies"]:
        body["mass"] = value(rng.choice([0.3, 0.5, 1, 2, 3, 5, 8]), "kg")
        a = next(a for a in s["annotations"] if a["id"] == body["label_ids"][0])
        a["geometry"]["text"] = (
            body["id"].replace("B", "m") if no_values else f"{body['mass']['number']:g} kg"
        )
        # Small independent body size variation, centred on the authored anchor.
        factor = rng.uniform(0.8, 1.2)
        x, y = body["anchor"]
        shift = [0.0, 0.0]
        sf = next((sf for sf in s["surfaces"] if sf["id"] == body["on_surface"]), None)
        if sf:
            startpoint, endpoint = sf["polyline"][0], sf["polyline"][-1]
            length = math.dist(startpoint, endpoint)
            normal = [
                (endpoint[1] - startpoint[1]) / length,
                -(endpoint[0] - startpoint[0]) / length,
            ]
            distance = (x - startpoint[0]) * normal[0] + (y - startpoint[1]) * normal[1]
            shift = [v * distance * (factor - 1) for v in normal]

        def resize(p):
            return [x + (p[0] - x) * factor + shift[0], y + (p[1] - y) * factor + shift[1]]

        for link in s["links"]:
            for end in ("a", "b"):
                if link[end]["ref"] == body["id"]:
                    link[end]["point"] = resize(link[end]["point"])
                    link["polyline"][0 if end == "a" else -1] = link[end]["point"]
        body["mask"] = [resize(p) for p in body["mask"]]
        box = body["bbox"]
        body["bbox"] = [
            *resize(box[:2]),
            *resize(box[2:]),
        ]
        body["anchor"] = [x + shift[0], y + shift[1]]
        a["geometry"]["bbox"] = [
            body["anchor"][0] - 16,
            body["anchor"][1] - 9,
            body["anchor"][0] + 58,
            body["anchor"][1] + 22,
        ]
    b = s["bodies"][0]
    x, y = b["anchor"]
    if not s["forces"]:
        s["forces"].append(
            {
                "id": "force_1",
                "body": b["id"],
                "tail": [x, y],
                "head": [x, y + 70],
                "magnitude": value(b["mass"]["number"] * 9.81, "N"),
                "label": "mg",
            }
        )
    s["annotations"].append(
        {
            "id": "velocity_1",
            "type": "axis",
            "geometry": {"points": [[x, y], [x + 90, y - rng.uniform(0, 45)]]},
        }
    )
    if rng.random() < 0.75 or s["archetype"] == "projectile":
        s["annotations"].append(
            {"id": "axis_1", "type": "axis", "geometry": {"points": [[65, 360], [65, 255]]}}
        )
    if s["archetype"] == "projectile":
        s["annotations"].append(
            {
                "id": "trajectory_1",
                "type": "axis",
                "geometry": {
                    "points": [[100 + v * 11, 440 - 8 * v + 0.12 * v * v] for v in range(51)]
                },
            }
        )
    s["annotations"].append(
        {"id": "dimension_1", "type": "dimension", "geometry": {"points": [[140, 530], [540, 530]]}}
    )
    if not no_values:
        length = float(f"{400 / s['frame']['px_per_m']['number']:.4g}")
        s["params"]["dimension_length"] = value(length, "m")
        label(s, "dimension_text", f"L = {length:g} m", 300, 538, "params.dimension_length")
        key = {
            "projectile": "launch_speed",
            "incline_block": "applied_force",
            "pendulum": "release_angle",
            "spring_mass": "initial_stretch",
            "atwood": "initial_speed",
            "table_pulley": "initial_speed",
            "incline_pulley": "initial_speed",
            "collision_1d": "restitution",
        }[s["archetype"]]
        physical = s["params"][key]
        label(
            s,
            "physical_text",
            f"{physical['number']:g} {physical['unit']}",
            rng.uniform(550, 650),
            rng.uniform(330, 410),
            "params." + key,
        )
    if not any(a["type"] == "angle_arc" for a in s["annotations"]) and s["archetype"] in {
        "projectile",
        "pendulum",
        "incline_pulley",
    }:
        if s["archetype"] == "pendulum":
            cx, cy = s["links"][0]["a"]["point"]
            start, end = 65, 90
        elif s["archetype"] == "incline_pulley":
            cx, cy = s["surfaces"][0]["polyline"][0]
            start, end = -30, 0
        else:
            cx, cy = x, y
            start, end = -45, 0
        s["annotations"].append(
            {
                "id": "angle_1",
                "type": "angle_arc",
                "geometry": {
                    "bbox": [cx - 30, cy - 30, cx + 30, cy + 30],
                    "start_deg": start,
                    "end_deg": end,
                },
            }
        )
    for a in s["annotations"]:
        if a["geometry"].get("text") and bengali:
            a["geometry"]["text"] = a["geometry"]["text"].translate(
                str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
            )
    s["repairs"] = []
    return Scene.model_validate(s)


def project_point(point, H):
    p = H @ np.array([*point, 1.0])
    return [float(p[0] / p[2]), float(p[1] / p[2])]


def transform_scene(scene, H, width, height, name, elastic=None):
    d = scene.model_dump(mode="json", by_alias=True)

    def p(v):
        point = project_point(v, H)
        return deform(point, elastic).tolist() if elastic else point

    def polyline(points, closed=False):
        if not elastic or len(points) < 2:
            return [p(v) for v in points]
        source = list(points) + ([points[0]] if closed else [])
        dense = []
        for a, b in zip(source, source[1:]):
            count = max(1, math.ceil(math.dist(a, b) / 10))
            dense.extend(
                [
                    [a[0] + (b[0] - a[0]) * t / count, a[1] + (b[1] - a[1]) * t / count]
                    for t in range(count)
                ]
            )
        return [p(v) for v in [*dense, source[-1]]]

    def box(b):
        points = [p([b[0], b[1]]), p([b[2], b[1]]), p([b[2], b[3]]), p([b[0], b[3]])]
        return [
            min(v[0] for v in points),
            min(v[1] for v in points),
            max(v[0] for v in points),
            max(v[1] for v in points),
        ]

    d["image"] = {"path": name, "width": width, "height": height}
    for b in d["bodies"]:
        b["anchor"] = p(b["anchor"])
        b["bbox"] = box(b["bbox"])
        b["mask"] = polyline(b["mask"], closed=True)
    for sf in d["surfaces"]:
        sf["polyline"] = polyline(sf["polyline"])
    for link in d["links"]:
        link["a"]["point"] = p(link["a"]["point"])
        link["b"]["point"] = p(link["b"]["point"])
        link["polyline"] = polyline(link["polyline"])
    for pulley in d["pulleys"]:
        centre = p(pulley["center"])
        radius = p([pulley["center"][0] + pulley["radius_px"], pulley["center"][1]])
        pulley["center"] = centre
        pulley["radius_px"] = math.dist(centre, radius)
    for a in d["annotations"]:
        g = a["geometry"]
        g["points"] = polyline(g["points"])
        if g["bbox"]:
            g["bbox"] = box(g["bbox"])
    for f in d["forces"]:
        f["tail"] = p(f["tail"])
        f["head"] = p(f["head"])
    # For photo/scan data the homography in the manifest is the exact geometry
    # transform. Physical priors are supervision, not a calibrated solver demo.
    d["frame"]["px_per_m"]["number"] *= math.sqrt(abs(np.linalg.det(H[:2, :2])))
    return Scene.model_validate(d)


def sample(source, spec, rng, name, *, handwriting="baseline"):
    if handwriting not in {"baseline", "strong"}:
        raise ValueError("Unknown handwriting profile")
    archetype, style, mirror, no_values, bengali = spec
    scene = variant(source, rng, no_values, bengali)
    raw = scene.model_dump(mode="json", by_alias=True)
    raw["frame"].update(
        paper_color=rng.choice(["#fffef7", "#f4f1e7", "#ffffff"]),
        ink_color=rng.choice(["#202c3a", "#30251d", "#183553"]),
        stroke_px=rng.uniform(1.5, 3.8),
    )
    raw["meta"].update(
        style="photo"
        if style == "photo"
        else "handwritten"
        if style == "handwritten"
        else "printed",
        language="bn" if bengali else "en",
    )
    scene = Scene.model_validate(raw)
    image, objects = render(
        scene,
        rng,
        style=style,
        font_size=rng.randint(14, 21),
        font_variant=int(bengali or rng.random() < 0.5),
        arrow_style=rng.choice(["filled", "open"]),
        hatch_spacing=rng.randint(11, 23),
        mirror_text=mirror,
        handwriting=handwriting,
    )
    # Record actual authored mask/text extents, not estimated text widths. The
    # masks come from our drawing commands; this is not automatic real annotation.
    raw = scene.model_dump(mode="json", by_alias=True)
    for obj in objects:
        bbox = list(obj["mask"].getbbox())
        for body in raw["bodies"]:
            if body["id"] == obj["id"]:
                body["bbox"] = bbox
                contours, _ = cv2.findContours(
                    np.array(obj["mask"]), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
                )
                polygon = max(contours, key=cv2.contourArea).reshape(-1, 2).tolist()
                if len(polygon) >= 3:
                    body["mask"] = polygon
        for a in raw["annotations"]:
            if a["id"] == obj["id"] and obj["class"] == "text_label":
                a["geometry"]["bbox"] = bbox
    scene = Scene.model_validate(raw)
    boxes = [o["mask"].getbbox() for o in objects]
    x0, y0 = min(b[0] for b in boxes) - 8, min(b[1] for b in boxes) - 8
    x1, y1 = max(b[2] for b in boxes) + 8, max(b[3] for b in boxes) + 8
    width, height = rng.randint(600, 1400), rng.randint(600, 1400)
    margin = rng.randint(55, 80)
    requested = rng.uniform(0.5, 1.6)
    scale = min(requested, (width - 2 * margin) / (x1 - x0), (height - 2 * margin) / (y1 - y0))
    if scale < 0.5:
        raise ValueError("Layout below required minimum scale")
    tx = rng.uniform(margin, width - margin - (x1 - x0) * scale) - x0 * scale
    ty = rng.uniform(margin, height - margin - (y1 - y0) * scale) - y0 * scale
    H = np.array([[scale, 0, tx], [0, scale, ty], [0, 0, 1.0]])
    if mirror:
        H = np.array([[-1.0, 0, width - 1], [0, 1.0, 0], [0, 0, 1.0]]) @ H
    if style == "scan":
        angle = rng.uniform(-3, 3)
        rotation = np.vstack(
            [cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1), [0, 0, 1]]
        )
        H = rotation @ H
    phone_photo = style == "photo" or (
        style == "handwritten" and handwriting == "strong" and rng.random() < 0.5
    )
    if phone_photo:
        src = np.float32([[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]])
        d = min(width, height) * 0.04
        dst = src + np.float32(
            [
                [rng.uniform(0, d), rng.uniform(0, d)],
                [-rng.uniform(0, d), rng.uniform(0, d)],
                [-rng.uniform(0, d), -rng.uniform(0, d)],
                [rng.uniform(0, d), -rng.uniform(0, d)],
            ]
        )
        H = cv2.getPerspectiveTransform(src, dst) @ H
    paper = tuple(int(scene.frame.paper_color[i : i + 2], 16) for i in (1, 3, 5))
    raster = cv2.warpPerspective(
        np.array(image), H, (width, height), flags=cv2.INTER_CUBIC, borderValue=paper
    )
    elastic = (
        elastic_parameters(rng) if style == "handwritten" and handwriting == "strong" else None
    )
    maps = inverse_maps(width, height, elastic) if elastic else None
    if maps is not None:
        raster = warp(raster, maps, border=paper)
    raster = texture(Image.fromarray(raster), rng, style)
    ruling = None
    if elastic:
        raster, ruling = notebook(raster, rng)
    if style in {"handwritten", "scan", "photo"}:
        raster = raster.filter(ImageFilter.GaussianBlur(rng.uniform(0.15, 0.55)))
    instances = np.zeros((height, width), np.uint16)
    transformed = []
    for i, o in enumerate(objects, 1):
        mask = cv2.warpPerspective(np.array(o["mask"]), H, (width, height), flags=cv2.INTER_NEAREST)
        if maps is not None:
            mask = warp(mask, maps, mask=True)
        yy, xx = np.where(mask > 0)
        if (
            not len(xx)
            or xx.min() <= 0
            or yy.min() <= 0
            or xx.max() >= width - 1
            or yy.max() >= height - 1
        ):
            raise ValueError("Object clipped at image boundary")
        bbox = [int(xx.min()), int(yy.min()), int(xx.max()) + 1, int(yy.max()) + 1]
        instances[mask > 0] = i
        transformed.append({"id": o["id"], "class": o["class"], "bbox": bbox, "mask_index": i})
    transformed_scene = transform_scene(scene, H, width, height, name, elastic)
    raw = transformed_scene.model_dump(mode="json", by_alias=True)
    for obj in transformed:
        for body in raw["bodies"]:
            if body["id"] == obj["id"]:
                body["bbox"] = obj["bbox"]
        for a in raw["annotations"]:
            if a["id"] == obj["id"] and obj["class"] == "text_label":
                a["geometry"]["bbox"] = obj["bbox"]
    transformed_scene = Scene.model_validate(raw)
    return (
        raster,
        instances,
        transformed,
        transformed_scene,
        {
            "homography": H.tolist(),
            "requested_scale": requested,
            "scale": scale,
            "mirrored": mirror,
            "no_numeric_values": no_values,
            "bengali_digits": bengali,
            "style": style,
            "archetype": archetype,
            "handwriting_profile": handwriting,
            "elastic": elastic,
            "notebook_ruling": ruling,
            "phone_photo": phone_photo,
        },
    )


def generate(output, count=600, seed=42, *, small=False, handwriting="baseline"):
    if not small and not 400 <= count <= 800:
        raise ValueError("R1 needs 400–800 images; --small is for tests/smoke only")
    out = fresh(output)
    for folder in ("images", "labels", "scenes", "masks", "objects"):
        (out / folder).mkdir()
    rng = random.Random(seed)
    templates = fixtures()
    by_type = {a: [s for s in templates.values() if s.archetype == a] for a in ARCHETYPES}
    rows = []
    class_counts = Counter()
    for i, spec in enumerate(schedules(count, seed)):
        archetype, style, *_ = spec
        name = f"synthetic_{i:04d}"
        extension = ".jpg" if style in {"scan", "photo"} else ".png"
        image, masks, objects, scene, settings = sample(
            rng.choice(by_type[archetype]), spec, rng, name + extension, handwriting=handwriting
        )
        image_path = out / "images" / (name + extension)
        image.save(
            image_path,
            **({"quality": rng.randint(72, 94), "subsampling": 0} if extension == ".jpg" else {}),
        )
        Image.fromarray(masks).save(out / "masks" / (name + ".png"))
        write_json(out / "objects" / (name + ".json"), objects)
        write_json(out / "scenes" / (name + ".json"), scene.model_dump(mode="json", by_alias=True))
        label_path = out / "labels" / (name + ".txt")
        label_path.write_text(
            "\n".join(yolo_line(o["class"], o["bbox"], *image.size) for o in objects) + "\n",
            encoding="utf-8",
        )
        class_counts.update(o["class"] for o in objects)
        rows.append(
            {
                "image": image_path.relative_to(out).as_posix(),
                "label": label_path.relative_to(out).as_posix(),
                "sha256": sha256(image_path),
                "label_sha256": sha256(label_path),
                "archetype": archetype,
                "style": style,
                "synthetic": True,
                "human_reviewed": False,
                "source_group": f"seed-{seed}-scene-{i}",
                "split": "train",
                "augmentation": settings,
            }
        )
    # Quarantine exact/near-duplicate connected components into a single split.
    groups = duplicate_groups([out / r["image"] for r in rows])
    for row in rows:
        group = groups[str(out / row["image"])]
        row["source_group"] = f"synthetic-{seed}-group-{group}"
        row["split"] = "val" if group % 5 == 0 else "train"
    if len({r["split"] for r in rows}) != 2:
        raise ValueError("No independent synthetic train/val groups")
    manifest = {
        "version": 1,
        "domain": "mechanics",
        "origin": "synthetic",
        "seed": seed,
        "class_names": list(NAMES),
        "records": rows,
        "benchmark_note": "Synthetic, not real accuracy; not frozen gold.",
        "near_duplicates_grouped": True,
    }
    write_json(out / "manifest.json", manifest)
    for split in ("train", "val"):
        (out / (split + ".txt")).write_text(
            "\n".join("./" + r["image"] for r in rows if r["split"] == split) + "\n",
            encoding="utf-8",
        )
    (out / "data.yaml").write_text(
        yaml.safe_dump(
            {"path": str(out), "train": "train.txt", "val": "val.txt", "names": list(NAMES)}
        ),
        encoding="utf-8",
    )
    counts = {
        "images": count,
        "classes": {n: class_counts[n] for n in NAMES},
        "archetypes": dict(Counter(r["archetype"] for r in rows)),
        "styles": dict(Counter(r["style"] for r in rows)),
        "splits": dict(Counter(r["split"] for r in rows)),
        "mirrored": sum(r["augmentation"]["mirrored"] for r in rows),
        "no_numeric_values": sum(r["augmentation"]["no_numeric_values"] for r in rows),
        "bengali_digits": sum(r["augmentation"]["bengali_digits"] for r in rows),
        "minimum_per_class": 40,
        "small_test_only": small,
    }
    if not small and min(class_counts[n] for n in NAMES) < 40:
        raise ValueError("Synthetic class minimum not met")
    if max(counts["archetypes"].values()) - min(counts["archetypes"].values()) > 1:
        raise AssertionError("Unbalanced archetypes")
    write_json(out / "counts.json", counts)
    (out / "SOURCE.md").write_text(
        "# Synthetic mechanics R1\n\nProgrammatically authored from M2 primitives. No real image or frozen gold used. "
        "This is synthetic, not a real benchmark. Native boxes are amodal drawn-object extents; indexed masks store visible object ids. "
        "Homographies preserve geometry supervision; augmented scenes are not calibrated solver demos. "
        "Shared templates/styles limit independence. Source groups keep exact/near duplicates together. "
        "Local bundled Pillow/Noto fonts; no font or model downloads.\n",
        encoding="utf-8",
    )
    contact_sheet(out, rows)
    return counts


def contact_sheet(root, rows):
    chosen = []
    for a in ARCHETYPES:
        for style in STYLES:
            row = next((r for r in rows if r["archetype"] == a and r["style"] == style), None)
            if row:
                chosen.append(row)
    sheet = Image.new("RGB", (4 * 320, math.ceil(len(chosen) / 4) * 260), "#e7e9ed")
    d = ImageDraw.Draw(sheet)
    for i, row in enumerate(chosen):
        x, y = (i % 4) * 320, (i // 4) * 260
        with Image.open(root / row["image"]) as im:
            im.thumbnail((306, 225))
            sheet.paste(im, (x + 7 + (306 - im.width) // 2, y + 25 + (225 - im.height) // 2))
        d.text((x + 7, y + 5), f"SYNTHETIC {row['archetype']} / {row['style']}", fill="#102b44")
    sheet.save(root / "contact-sheet.jpg", quality=92)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--count", type=int, default=600)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--small", action="store_true")
    p.add_argument("--handwriting", choices=["baseline", "strong"], default="baseline")
    args = p.parse_args()
    print(
        json.dumps(
            generate(
                args.out, args.count, args.seed, small=args.small, handwriting=args.handwriting
            ),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
