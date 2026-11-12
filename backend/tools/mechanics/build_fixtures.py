"""Build exactly ten authored synthetic fixtures and the canonical scene schema."""

import json
import math
from pathlib import Path

from ...domains.mechanics.scene import Scene
from .paint_scene import save_diagram

ROOT = Path(__file__).resolve().parents[3]


def value(number, unit="1", status="given", source="user"):
    return dict(number=float(number), unit=unit, status=status, source=source, confidence=1.0)


def vector(x, y, unit):
    return dict(x=value(x, unit), y=value(y, unit))


def rectangle(x, y, w, h, angle=0):
    c, s = math.cos(angle), math.sin(angle)
    return [
        (x + dx * c - dy * s, y + dx * s + dy * c)
        for dx, dy in [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    ]


def body(
    scene,
    id,
    anchor,
    position=(0, 0),
    velocity=(0, 0),
    mass=1,
    kind="block",
    size=(60, 40),
    angle=0,
    surface=None,
):
    x, y = anchor
    mask = rectangle(x, y, *size, angle)
    bbox = (
        min(p[0] for p in mask),
        min(p[1] for p in mask),
        max(p[0] for p in mask),
        max(p[1] for p in mask),
    )
    label = f"label_{id}"
    scene["bodies"].append(
        dict(
            id=id,
            type=kind,
            bbox=bbox,
            mask=mask,
            anchor=anchor,
            label_ids=[label],
            mass=value(mass, "kg"),
            on_surface=surface,
            initial=dict(position=vector(*position, "m"), velocity=vector(*velocity, "m/s")),
        )
    )
    text(scene, label, f"{mass:g} kg", (x - 18, y - 8, x + 22, y + 12))


def text(scene, id, content, bbox, bound_to=None):
    scene["annotations"].append(
        dict(id=id, type="label", geometry=dict(text=content, bbox=bbox), bound_to=bound_to)
    )


def surface(scene, id, kind, points, angle=None, length=None, mu_s=0, mu_k=0):
    scene["surfaces"].append(
        dict(
            id=id,
            type=kind,
            polyline=points,
            angle_deg=value(angle, "deg") if angle is not None else None,
            length_m=value(length, "m") if length is not None else None,
            mu_s=value(mu_s),
            mu_k=value(mu_k),
        )
    )


def link(scene, kind, a, b, points, **kwargs):
    scene["links"].append(
        dict(
            id="L1",
            type=kind,
            a=dict(ref=a, point=points[0]),
            b=dict(ref=b, point=points[-1]),
            polyline=points,
            **kwargs,
        )
    )


def bind(scene, id, path, kind, low, high, step, unit, handle=None, labels=None):
    scene["bindings"].append(
        dict(
            id=id,
            path=path,
            **{"class": kind},
            control=dict(min=low, max=high, step=step, unit=unit, locked=kind == "geometry"),
            labels=labels or [],
            handle=handle,
        )
    )


def arc(center, radius, start, end, n=40):
    return [
        (
            center[0] + radius * math.cos(start + (end - start) * i / n),
            center[1] + radius * math.sin(start + (end - start) * i / n),
        )
        for i in range(n + 1)
    ]


def base(name, archetype, scale):
    scene = dict(
        image=dict(path=f"{name}.png", width=800, height=520),
        archetype=archetype,
        frame=dict(px_per_m=value(scale, "px/m", "assumed", "prior")),
        bodies=[],
        surfaces=[],
        links=[],
        pulleys=[],
        annotations=[],
        forces=[],
        bindings=[],
        repairs=[],
        params={},
        constraints=[],
        meta=dict(style="printed", provenance="authored", language="en"),
    )
    text(scene, "title", f"SYNTHETIC / AUTHORED: {name.replace('_', ' ')}", (20, 16, 760, 40))
    return scene


def fixtures():
    result = {}
    for cliff in (False, True):
        name = "projectile_cliff" if cliff else "projectile_ground"
        s = base(name, "projectile", 14)
        h = 6 if cliff else 0
        surface(s, "S1", "floor", [(35, 453), (770, 453)])
        if cliff:
            surface(s, "S2", "wall", [(100, 453), (100, 453 - h * 14)])
            surface(s, "S3", "floor", [(35, 453 - h * 14), (100, 453 - h * 14)])
        body(s, "B1", (100, 440 - h * 14), position=(0, -h), kind="ball", size=(26, 26))
        s["params"] = dict(
            launch_speed=value(20, "m/s"),
            launch_angle=value(45, "deg"),
            launch_height=value(h, "m"),
        )
        s["annotations"].append(
            dict(
                id="launch",
                type="axis",
                geometry=dict(points=[(100, 440 - h * 14), (150, 390 - h * 14)]),
            )
        )
        for key, lo, hi, unit in [
            ("launch_speed", 1, 40, "m/s"),
            ("launch_angle", 5, 85, "deg"),
            ("launch_height", 0, 20, "m"),
        ]:
            bind(
                s,
                key,
                f"params.{key}",
                "geometry" if cliff and key == "launch_height" else "initial",
                lo,
                hi,
                0.1,
                unit,
                "launch" if key != "launch_height" else None,
            )
        result[name] = s
    s = base("incline", "incline_block", 160)
    theta, q = math.pi / 6, 1.8
    u = (math.cos(theta), -math.sin(theta))
    n = (-math.sin(theta), -math.cos(theta))
    foot = (100, 440)
    top = (foot[0] + 480 * u[0], foot[1] + 480 * u[1])
    surface(s, "S1", "incline", [foot, top], 30, 3, 0.25, 0.2)
    surface(s, "S2", "floor", [(40, 440), (760, 440)])
    p = (foot[0] + q * 160 * u[0] + 20 * n[0], foot[1] + q * 160 * u[1] + 20 * n[1])
    body(s, "B1", p, position=(q * u[0], q * u[1]), mass=5, angle=-theta, surface="S1")
    s["params"] = dict(
        start_position=value(q, "m"), initial_speed=value(0, "m/s"), applied_force=value(0, "N")
    )
    s["annotations"].append(
        dict(
            id="angle",
            type="angle_arc",
            geometry=dict(bbox=(70, 410, 130, 470), start_deg=-30, end_deg=0),
        )
    )
    bind(s, "position", "params.start_position", "initial", 0.2, 2.8, 0.01, "m", "block")
    bind(s, "theta", "surfaces.S1.angle_deg", "geometry", 5, 75, 1, "deg", "incline_tip")
    bind(s, "length", "surfaces.S1.length_m", "geometry", 1, 4, 0.1, "m")
    bind(s, "mu", "surfaces.S1.mu_k", "physics", 0, 1, 0.01, "1")
    bind(s, "force", "params.applied_force", "physics", -100, 100, 1, "N")
    result["incline"] = s
    s = base("pendulum", "pendulum", 250)
    pivot = (370, 90)
    angle = math.radians(25)
    p = (pivot[0] + 250 * math.sin(angle), pivot[1] + 250 * math.cos(angle))
    surface(s, "S1", "ceiling", [(270, 80), (470, 80)])
    s["annotations"].append(dict(id="pivot", type="axis", geometry=dict(points=[pivot])))
    body(s, "B1", p, position=(math.sin(angle), math.cos(angle)), kind="bob", size=(48, 48))
    link(s, "rod", "pivot", "B1", [pivot, p], length_m=value(1, "m"), damping=value(0, "1/s"))
    s["params"] = dict(release_angle=value(25, "deg"), angular_speed=value(0, "rad/s"))
    bind(s, "angle", "params.release_angle", "initial", -70, 70, 1, "deg", "bob")
    bind(s, "length", "links.L1.length_m", "initial", 0.25, 1.5, 0.01, "m")
    bind(s, "damping", "links.L1.damping", "physics", 0, 3, 0.01, "1/s")
    result["pendulum"] = s
    for vertical in (False, True):
        name = "spring_vertical" if vertical else "spring_horizontal"
        s = base(name, "spring_mass", 240)
        support = (400, 90) if vertical else (140, 330)
        end = (400, 258) if vertical else (308, 330)
        p = (end[0], end[1] + 25) if vertical else (end[0] + 30, end[1])
        surface(
            s,
            "S1",
            "ceiling" if vertical else "wall",
            [(300, 80), (500, 80)] if vertical else [(140, 230), (140, 400)],
        )
        if not vertical:
            surface(s, "S2", "floor", [(140, 350), (750, 350)])
        s["annotations"].append(dict(id="support", type="axis", geometry=dict(points=[support])))
        body(
            s,
            "B1",
            p,
            position=(0, 0.2) if vertical else (0.2, 0),
            size=(60, 50) if vertical else (60, 40),
        )
        link(
            s,
            "spring",
            "support",
            "B1",
            [support, end],
            k=value(100, "N/m"),
            rest_length_m=value(0.5, "m", "assumed", "prior"),
            coils=10,
            damping=value(0, "kg/s"),
        )
        s["params"] = dict(
            initial_stretch=value(0.2, "m"),
            initial_speed=value(0, "m/s"),
            vertical=value(int(vertical)),
        )
        bind(
            s, "stretch", "params.initial_stretch", "initial", -0.35, 0.65, 0.01, "m", "spring_end"
        )
        bind(s, "k", "links.L1.k", "physics", 10, 500, 1, "N/m")
        bind(s, "damping", "links.L1.damping", "physics", 0, 30, 0.1, "kg/s")
        result[name] = s
    s = base("atwood", "atwood", 100)
    s["pulleys"].append(dict(id="P1", center=(400, 130), radius_px=50))
    surface(s, "S1", "floor", [(250, 470), (550, 470)])
    body(s, "B1", (350, 300), position=(0, 0), mass=1)
    body(s, "B2", (450, 300), position=(1, 0), mass=2)
    link(
        s,
        "rope",
        "B1",
        "B2",
        [(350, 280)] + arc((400, 130), 50, math.pi, 2 * math.pi) + [(450, 280)],
    )
    s["params"] = dict(initial_speed=value(0, "m/s"))
    result["atwood"] = s
    s = base("table_pulley", "table_pulley", 100)
    surface(s, "S1", "floor", [(70, 260), (580, 260)], mu_s=0.15, mu_k=0.1)
    surface(s, "S2", "floor", [(580, 480), (750, 480)])
    surface(s, "S3", "wall", [(580, 260), (580, 480)])
    s["pulleys"].append(dict(id="P1", center=(580, 270), radius_px=30))
    body(s, "B1", (280, 240), mass=2, surface="S1")
    body(s, "B2", (610, 360), position=(3.3, 1.2), mass=1)
    link(s, "rope", "B1", "B2", [(310, 240)] + arc((580, 270), 30, -math.pi / 2, 0) + [(610, 340)])
    s["params"] = dict(initial_speed=value(0, "m/s"))
    bind(s, "mu", "surfaces.S1.mu_k", "physics", 0, 1, 0.01, "1")
    result["table_pulley"] = s
    s = base("incline_pulley", "incline_pulley", 150)
    theta = math.pi / 6
    u, n = (math.cos(theta), -math.sin(theta)), (-math.sin(theta), -math.cos(theta))
    basepoint = (100, 440)
    top = (100 + 450 * u[0], 440 + 450 * u[1])
    center = (top[0] - 12 * n[0], top[1] - 12 * n[1])
    surface(s, "S1", "incline", [basepoint, top], 30, 3, 0.1, 0.1)
    surface(s, "S2", "floor", [(40, 480), (740, 480)])
    s["pulleys"].append(dict(id="P1", center=center, radius_px=30))
    p = (100 + 180 * u[0] + 18 * n[0], 440 + 180 * u[1] + 18 * n[1])
    body(s, "B1", p, position=(0, 0), mass=2, size=(60, 36), angle=-theta, surface="S1")
    body(s, "B2", (center[0] + 30, 365), position=(2, 1), mass=2)
    start = (p[0] + 30 * u[0], p[1] + 30 * u[1])
    # Ramp normal points up-left: tangent follows the incline to the upper arc.
    rope_arc = arc(center, 30, math.atan2(n[1], n[0]), 0)
    link(s, "rope", "B1", "B2", [start] + rope_arc + [(center[0] + 30, 345)])
    s["params"] = dict(initial_speed=value(0, "m/s"))
    bind(s, "theta", "surfaces.S1.angle_deg", "geometry", 10, 60, 1, "deg", "incline_tip")
    result["incline_pulley"] = s
    s = base("collision", "collision_1d", 100)
    surface(s, "S1", "floor", [(40, 360), (760, 360)])
    body(
        s,
        "B1",
        (200, 340),
        position=(0, 0),
        velocity=(2, 0),
        kind="cart",
        size=(50, 40),
        surface="S1",
    )
    body(
        s,
        "B2",
        (400, 340),
        position=(2, 0),
        velocity=(-1, 0),
        kind="cart",
        size=(50, 40),
        surface="S1",
    )
    s["params"] = dict(restitution=value(1))
    bind(s, "e", "params.restitution", "physics", 0, 1, 0.01, "1")
    bind(s, "v1", "bodies.B1.initial.velocity.x", "initial", -5, 5, 0.1, "m/s")
    bind(s, "v2", "bodies.B2.initial.velocity.x", "initial", -5, 5, 0.1, "m/s")
    result["collision"] = s
    for s in result.values():
        for sf in s["surfaces"]:
            if sf["mu_s"]["number"] > 0:
                bind(s, "mu_static", f"surfaces.{sf['id']}.mu_s", "physics", 0, 1, 0.01, "1")
        for b in s["bodies"]:
            bind(
                s,
                f"mass_{b['id']}",
                f"bodies.{b['id']}.mass",
                "physics",
                0.1,
                10,
                0.1,
                "kg",
                labels=b["label_ids"],
            )
        bind(s, "g", "constants.g", "physics", 0.1, 20, 0.01, "m/s^2")
        # Explicit static-line repairs under source masks. These are authored,
        # not inferred from automatic labels or used as real-image annotations.
        for sf in s["surfaces"]:
            a, b = sf["polyline"][0], sf["polyline"][-1]
            dx, dy = b[0] - a[0], b[1] - a[1]
            segments = []
            boxes = [body["bbox"] for body in s["bodies"]]
            for pulley in s["pulleys"]:
                x, y = pulley["center"]
                r = pulley["radius_px"] + 3
                boxes.append((x - r, y - r, x + r, y + r))
            if s["archetype"] == "spring_mass":
                x, y = s["links"][0]["a"]["point"]
                boxes.append((x - 3, y - 16, x + 3, y + 16))
            for x0, y0, x1, y1 in boxes:
                lo, hi = 0.0, 1.0
                for origin, delta, lower, upper in [
                    (a[0], dx, x0 - 5, x1 + 5),
                    (a[1], dy, y0 - 5, y1 + 5),
                ]:
                    if abs(delta) < 1e-12:
                        if not lower <= origin <= upper:
                            hi = -1
                    else:
                        t0, t1 = (lower - origin) / delta, (upper - origin) / delta
                        lo, hi = max(lo, min(t0, t1)), min(hi, max(t0, t1))
                if lo < hi:
                    segments.append(
                        [(a[0] + lo * dx, a[1] + lo * dy), (a[0] + hi * dx, a[1] + hi * dy)]
                    )
            if segments:
                s["repairs"].append(dict(surface_or_line_id=sf["id"], segments=segments))
        row = 0
        for binding in s["bindings"]:
            if binding["labels"] or binding["id"] == "g":
                continue
            v = s
            for part in binding["path"].split("."):
                v = next(obj for obj in v if obj["id"] == part) if isinstance(v, list) else v[part]
            label = "param_" + binding["id"]
            text(
                s,
                label,
                f"{binding['id']}: {v['number']:g} {v['unit']}",
                (570, 65 + row * 23, 790, 86 + row * 23),
                binding["path"],
            )
            binding["labels"].append(label)
            row += 1
    return {name: Scene.model_validate(raw) for name, raw in result.items()}


def main():
    destination = ROOT / "fixtures" / "mechanics"
    destination.mkdir(parents=True, exist_ok=True)
    for name, scene in fixtures().items():
        save_diagram(scene, destination / f"{name}.png")
    (ROOT / "docs/mechanics/schema.json").write_text(
        json.dumps(Scene.model_json_schema(mode="serialization", by_alias=True), indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(fixtures())} synthetic JSON/PNG pairs and schema")


if __name__ == "__main__":
    main()
