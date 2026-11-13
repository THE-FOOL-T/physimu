"""Opt-in synthetic appearance diversity; never labels from a real image."""

import math

from ...domains.mechanics.scene import Scene


FILLS = ("#e7c870", "#93becd", "#c7b2d9", "#c8c8c8", "#f1b0a2")


def separate(a, b, gap=8):
    return a[2] + gap < b[0] or b[2] + gap < a[0] or a[3] + gap < b[1] or b[3] + gap < a[1]


def place_body_labels(raw, rng):
    ids = {body["label_ids"][0] for body in raw["bodies"]}
    occupied = [
        a["geometry"]["bbox"]
        for a in raw["annotations"]
        if a["type"] == "label" and a["id"] not in ids
    ]
    for body in raw["bodies"]:
        annotation = next(a for a in raw["annotations"] if a["id"] == body["label_ids"][0])
        width, height = max(34, len(annotation["geometry"]["text"]) * 28), 52
        x0, y0, x1, y1 = body["bbox"]
        cx, cy = body["anchor"]
        candidates = [
            [x0 - width - 16, cy - height / 2],
            [x1 + 16, cy - height / 2],
            [cx - width / 2, y0 - height - 16],
            [cx - width / 2, y1 + 24],
        ]
        rng.shuffle(candidates)
        if x1 - x0 >= width + 16 and y1 - y0 >= height + 16 and rng.random() < 0.4:
            candidates.insert(0, [cx - width / 2, cy - height / 2])
        for x, y in candidates:
            box = [x, y, x + width, y + height]
            inside = x >= x0 + 8 and y >= y0 + 8 and x + width <= x1 - 8 and y + height <= y1 - 8
            bodies = [b["bbox"] for b in raw["bodies"] if not (inside and b["id"] == body["id"])]
            if (
                8 <= x
                and 8 <= y
                and x + width < raw["image"]["width"] - 8
                and y + height < raw["image"]["height"] - 8
                and all(separate(box, b) for b in [*occupied, *bodies])
            ):
                annotation["geometry"]["bbox"] = box
                occupied.append(box)
                break
        else:
            raise ValueError("No clear position for synthetic body label")


def prepare(scene, rng):
    """Enlarge drawn objects and vary labels without moving contact/attachment points apart."""
    raw = scene.model_dump(mode="json", by_alias=True)
    for body in raw["bodies"]:
        x, y = body["anchor"]
        factor = rng.uniform(1.2, 2.0)
        if raw["archetype"] == "atwood":
            # Keep suspended bodies separate before making their drawings larger.
            width = body["bbox"][2] - body["bbox"][0]
            factor = min(
                factor,
                *(
                    0.8 * abs(x - other["anchor"][0]) / width
                    for other in raw["bodies"]
                    if other["id"] != body["id"]
                ),
            )
        shift = [0.0, 0.0]
        surface = next((s for s in raw["surfaces"] if s["id"] == body["on_surface"]), None)
        if surface:
            a, b = surface["polyline"][0], surface["polyline"][-1]
            length = math.dist(a, b)
            normal = [(b[1] - a[1]) / length, -(b[0] - a[0]) / length]
            distance = (x - a[0]) * normal[0] + (y - a[1]) * normal[1]
            shift = [v * distance * (factor - 1) for v in normal]

        def resize(point):
            return [x + (point[0] - x) * factor + shift[0], y + (point[1] - y) * factor + shift[1]]

        body["mask"] = [resize(p) for p in body["mask"]]
        body["bbox"] = [*resize(body["bbox"][:2]), *resize(body["bbox"][2:])]
        body["anchor"] = [x + shift[0], y + shift[1]]
        for link in raw["links"]:
            for end, index in (("a", 0), ("b", -1)):
                if link[end]["ref"] == body["id"]:
                    link[end]["point"] = resize(link[end]["point"])
                    link["polyline"][index] = link[end]["point"]
        for force in raw["forces"]:
            if force["body"] == body["id"]:
                force["tail"] = resize(force["tail"])
                force["head"] = resize(force["head"])
    place_body_labels(raw, rng)
    for link in raw["links"]:
        if link["type"] == "spring":
            link["coils"] = rng.randint(5, 16)
    for annotation in raw["annotations"]:
        geometry = annotation["geometry"]
        if annotation["type"] == "angle_arc":
            x0, y0, x1, y1 = geometry["bbox"]
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            radius = rng.uniform(45, 75)
            geometry["bbox"] = [cx - radius, cy - radius, cx + radius, cy + radius]
    # Standalone glyphs are text targets, including the letters mistaken for
    # bodies in the public previews. They are never labelled as physical bodies.
    occupied = [b["bbox"] for b in raw["bodies"]]
    occupied.extend(a["geometry"]["bbox"] for a in raw["annotations"] if a["geometry"]["bbox"])
    for collection in (raw["surfaces"], raw["links"]):
        for item in collection:
            points = item["polyline"]
            occupied.append(
                [
                    min(p[0] for p in points),
                    min(p[1] for p in points),
                    max(p[0] for p in points),
                    max(p[1] for p in points),
                ]
            )
    for pulley in raw["pulleys"]:
        x, y = pulley["center"]
        r = pulley["radius_px"]
        occupied.append([x - r, y - r, x + r, y + r])
    for i, text in enumerate(rng.sample(["m", "M", "N", "k", "x", "v"], 4)):
        for _ in range(200):
            x, y = rng.uniform(40, 820), rng.uniform(45, 550)
            box = [x, y, x + 64, y + 54]
            if all(
                box[2] + 8 < b[0] or b[2] + 8 < box[0] or box[3] + 8 < b[1] or b[3] + 8 < box[1]
                for b in occupied
            ):
                break
        else:
            raise ValueError("No clear paper for synthetic standalone text")
        occupied.append(box)
        raw["annotations"].append(
            dict(
                id=f"standalone_text_{i}",
                type="label",
                geometry=dict(text=text, bbox=box),
            )
        )
    if rng.random() < 0.5:
        raw["forces"] = []
    if rng.random() < 0.5:
        raw["annotations"] = [a for a in raw["annotations"] if not a["id"].startswith("velocity_")]
    return Scene.model_validate(raw)


def spring_path(a, b, coils, amplitude, curved):
    """Zigzag and sinusoidal coils with the same exact two native endpoints."""
    from .paint_scene import spring_points

    if not curved:
        return spring_points(a, b, coils, amplitude)
    length = math.dist(a, b)
    if length <= 24:
        return [a, b]
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    points = [a, (a[0] + ux * 12, a[1] + uy * 12)]
    count = coils * 24
    for i in range(count + 1):
        t = i / count
        phase = 2 * math.pi * coils * t
        distance = 12 + (length - 24) * t + amplitude * 0.25 * math.sin(phase)
        offset = amplitude * math.sin(phase)
        points.append((a[0] + ux * distance - uy * offset, a[1] + uy * distance + ux * offset))
    return [*points, (b[0] - ux * 12, b[1] - uy * 12), b]
