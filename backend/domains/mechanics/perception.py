"""Build editable scene objects from measurements, then calibrate browser inputs."""

import copy
import math

import numpy as np

from . import geometry, sprites
from .defaults import assumed
from .validate import warning


def value(n, unit, confidence=0.8, source="geometry", status="given"):
    return dict(
        number=float(n) if n is not None else None,
        unit=unit,
        status=status,
        source=source,
        confidence=float(confidence),
    )


def zero(unit):
    return value(0.0, unit, 0.0, "prior", "assumed")


def blank(image, lang="en", style="unknown"):
    h, w = image.shape[:2]
    return dict(
        version=1,
        domain="mechanics",
        image=dict(path="", width=w, height=h),
        archetype="unsupported",
        frame=dict(
            gravity=[0.0, 1.0],
            px_per_m=value(100.0, "px/m", 0.0, "prior", "assumed"),
            **geometry.measure_style(image),
        ),
        bodies=[],
        surfaces=[],
        links=[],
        pulleys=[],
        forces=[],
        annotations=[],
        repairs=[],
        constants=dict(g=assumed("g")),
        params={},
        bindings=[],
        constraints=[],
        warnings=[],
        meta=dict(language=lang, style=style, provenance="unsupported", region=None),
    )


def measure(image, detections, lang, style, check):
    scene = blank(image, lang, style)
    evidence = {}
    link_choices = {}
    counts = {}

    def id_(prefix):
        counts[prefix] = counts.get(prefix, 0) + 1
        return prefix + str(counts[prefix])

    texts = [d.bbox for d in detections if d.type == "text_label"]
    bodies = [d.bbox for d in detections if d.type in {"block", "ball", "bob", "cart"}]
    identity = {}

    def unknown(d, code):
        ref = id_("U")
        scene["annotations"].append(
            dict(id=ref, type="unresolved_" + d.type, geometry=dict(bbox=d.bbox))
        )
        warning(scene, code, ref)
        identity[d.id] = ref

    for d in detections:
        check()
        if d.type not in {"floor", "incline", "wall", "ceiling", "pulley"}:
            continue
        try:
            if d.type == "pulley":
                fit = geometry.fit_circle(image, d.bbox)
                ref = id_("P")
                scene["pulleys"].append(
                    dict(id=ref, center=fit["center"], radius_px=fit["radius_px"], mass=None)
                )
            else:
                fit = geometry.fit_line(image, d.bbox, [*texts, *bodies], orientation=d.type)
                ref = id_("S")
                scene["surfaces"].append(
                    dict(
                        id=ref,
                        type=d.type,
                        polyline=fit["points"],
                        angle_deg=value(fit["angle_deg"], "deg", fit["confidence"])
                        if d.type == "incline"
                        else None,
                        length_m=None,
                        mu_s=assumed("mu"),
                        mu_k=assumed("mu"),
                    )
                )
            identity[d.id] = ref
            evidence[ref] = fit
        except ValueError as error:
            unknown(d, str(error))
    lines = [(sf["polyline"][0], sf["polyline"][-1]) for sf in scene["surfaces"]]
    floor = next((evidence[s["id"]] for s in scene["surfaces"] if s["type"] == "floor"), None)
    if floor:
        for surface in scene["surfaces"]:
            if surface["type"] == "incline":
                surface["angle_deg"]["number"] -= floor["angle_deg"]
    for d in detections:
        check()
        if d.type not in {"block", "ball", "bob", "cart"}:
            continue
        fit = sprites.body_mask(image, d.bbox, lines)
        ref = id_("B")
        polygon = fit["polygon"]
        anchor = np.mean(polygon, axis=0).tolist()
        if d.type in {"ball", "bob"}:
            try:
                anchor = geometry.fit_circle(image, d.bbox)["center"]
            except ValueError:
                pass
        # Use a polygon centroid for uneven contour sampling.
        import cv2

        moments = cv2.moments(np.array(polygon, np.float32))
        if d.type not in {"ball", "bob"} and moments["m00"]:
            anchor = [moments["m10"] / moments["m00"], moments["m01"] / moments["m00"]]
        scene["bodies"].append(
            dict(
                id=ref,
                type=d.type,
                bbox=list(map(float, d.bbox)),
                mask=polygon,
                anchor=anchor,
                label_ids=[],
                mass=assumed("mass"),
                radius_m=None,
                on_surface=None,
                initial=dict(
                    position=dict(x=zero("m"), y=zero("m")),
                    velocity=dict(x=zero("m/s"), y=zero("m/s")),
                ),
            )
        )
        if fit["warning"]:
            warning(scene, fit["warning"], ref)
        identity[d.id] = ref
        evidence[ref] = fit
    for d in detections:
        if d.type == "pivot":
            ref = (
                "pivot"
                if not any(a["id"] == "pivot" for a in scene["annotations"])
                else id_("pivot_")
            )
            scene["annotations"].append(
                dict(
                    id=ref,
                    type="axis",
                    geometry=dict(
                        points=[[(d.bbox[0] + d.bbox[2]) / 2, (d.bbox[1] + d.bbox[3]) / 2]],
                        bbox=d.bbox,
                    ),
                )
            )
            identity[d.id] = ref
    exclusions = [
        *texts,
        *bodies,
        *[
            [
                p["center"][0] - p["radius_px"] - 2,
                p["center"][1] - p["radius_px"] - 2,
                p["center"][0] + p["radius_px"] + 2,
                p["center"][1] + p["radius_px"] + 2,
            ]
            for p in scene["pulleys"]
        ],
    ]
    for d in detections:
        check()
        if d.type not in {"rope", "rod", "spring"}:
            continue
        try:
            fit = (
                geometry.spring(image, d.bbox, exclusions)
                if d.type == "spring"
                else geometry.trace(image, d.bbox, exclusions)
            )
            points = np.array(fit["endpoints"] if d.type == "spring" else fit["points"])
            ref = id_("L")
            nearest = sorted(
                scene["bodies"],
                key=lambda b: float(np.linalg.norm(points - np.array(b["anchor"]), axis=1).min()),
            )
            if not nearest:
                raise ValueError("attachment_unreached")
            if scene["pulleys"] and len(nearest) >= 2 and d.type == "rope":
                selected = sorted(nearest[:2], key=lambda b: b["anchor"][0])
                start, end = [
                    points[
                        np.argmin(np.linalg.norm(points - np.array(b["anchor"]), axis=1))
                    ].tolist()
                    for b in selected
                ]
                a, b = [o["id"] for o in selected]
                p = scene["pulleys"][0]
                cx, cy = p["center"]
                r = p["radius_px"]
                arc = [
                    [cx + r * math.cos(t), cy + r * math.sin(t)]
                    for t in np.linspace(math.pi, 2 * math.pi, 33)
                ]
                route = [start, *arc, end]
                link_choices[ref] = [
                    (a, b, 0.0),
                    (
                        b,
                        a,
                        math.dist(start, selected[1]["anchor"])
                        + math.dist(end, selected[0]["anchor"]),
                    ),
                ]
                warning(scene, "rope_route_assumed", ref)
            else:
                body = nearest[0]
                anchor = np.array(body["anchor"])
                end = points[np.argmin(np.linalg.norm(points - anchor, axis=1))].tolist()
                piv = next((a for a in scene["annotations"] if a["id"] == "pivot"), None)
                if piv and d.type in {"rope", "rod"}:
                    start = piv["geometry"]["points"][0]
                    end = body["anchor"]
                    a, b = "pivot", body["id"]
                else:
                    start = points[np.argmax(np.linalg.norm(points - anchor, axis=1))].tolist()
                    a, b = id_("support_"), body["id"]
                    scene["annotations"].append(
                        dict(id=a, type="axis", geometry=dict(points=[start]))
                    )
                route = [start, end] if d.type == "spring" or piv else max(fit["segments"], key=len)
                if math.dist(route[0], start) > math.dist(route[-1], start):
                    route = route[::-1]
                route[0], route[-1] = start, end
            link = dict(
                id=ref,
                type=d.type,
                a=dict(ref=a, point=start),
                b=dict(ref=b, point=end),
                polyline=route,
                length_m=None,
                k=assumed("spring_constant") if d.type == "spring" else None,
                rest_length_m=assumed("spring_rest_length") if d.type == "spring" else None,
                coils=fit.get("coils"),
                damping=assumed("damping") if d.type == "spring" else None,
            )
            scene["links"].append(link)
            identity[d.id] = ref
            evidence[ref] = fit
        except ValueError as error:
            unknown(d, str(error))
    for d in detections:
        check()
        if d.id in identity:
            continue
        ref = id_("T")
        try:
            if d.type in {"arrow_force", "arrow_velocity", "axis", "dimension_line"}:
                fit = geometry.fit_line(image, d.bbox, texts)
                points = fit["points"]
                # Arrowhead has more ink than its tail in a small endpoint neighbourhood.
                ink = geometry.foreground(image)

                def density(p):
                    x, y = map(round, p)
                    return np.count_nonzero(ink[max(0, y - 8) : y + 9, max(0, x - 8) : x + 9])

                if density(points[0]) > density(points[-1]):
                    points = points[::-1]
                if d.type in {"arrow_force", "arrow_velocity"} and scene["bodies"]:

                    def nearest(p):
                        return min(math.dist(p, b["anchor"]) for b in scene["bodies"])

                    if nearest(points[0]) > nearest(points[-1]):
                        points = points[::-1]
                if d.type == "arrow_force" and scene["bodies"]:
                    body = min(scene["bodies"], key=lambda b: math.dist(b["anchor"], points[0]))
                    scene["forces"].append(
                        dict(
                            id=ref,
                            body=body["id"],
                            tail=points[0],
                            head=points[-1],
                            magnitude=None,
                            label="force",
                        )
                    )
                else:
                    ref = (
                        "velocity_"
                        if d.type == "arrow_velocity"
                        else "dimension_"
                        if d.type == "dimension_line"
                        else "axis_"
                    ) + ref
                    scene["annotations"].append(
                        dict(
                            id=ref,
                            type="dimension" if d.type == "dimension_line" else "axis",
                            geometry=dict(points=points, bbox=d.bbox),
                        )
                    )
                evidence[ref] = fit
            elif d.type == "trajectory_arc":
                fit = geometry.trajectory_arc(
                    image, d.bbox, scene["bodies"][0]["anchor"] if scene["bodies"] else None, texts
                )
                ref = "trajectory_" + ref
                scene["annotations"].append(
                    dict(id=ref, type="axis", geometry=dict(points=fit["points"], bbox=d.bbox))
                )
                evidence[ref] = fit
            else:
                kind = {
                    "text_label": "label",
                    "angle_mark": "angle_arc",
                    "ground_hatch": "ground_hatch",
                }.get(d.type, d.type)
                scene["annotations"].append(dict(id=ref, type=kind, geometry=dict(bbox=d.bbox)))
                if d.type not in {"text_label", "angle_mark", "ground_hatch"}:
                    warning(scene, "unknown_type", ref)
            identity[d.id] = ref
        except ValueError as error:
            unknown(d, str(error))
    confidences = {identity[d.id]: d.confidence for d in detections if d.id in identity}
    return scene, evidence, link_choices, confidences


def calibrate(scene, assignments, evidence):
    """Calibrate geometry and explicit priors, never overwrite a user/observed Value."""
    kind = scene["archetype"]
    bodies = scene["bodies"]
    links = scene["links"]
    params = scene["params"]
    S = 100.0
    measured = False
    for row in assignments:
        if not row["accepted"] or row["kind"] != "length":
            continue
        length = row["number"]
        if length is None or length <= 0:
            continue
        obj = next(
            (a for a in scene["annotations"] if a["id"] == row["ref"] and a["type"] == "dimension"),
            None,
        )
        link = next((link for link in links if link["id"] == row["ref"]), None)
        points = obj["geometry"]["points"] if obj else link["polyline"] if link else None
        if points:
            S = sum(math.dist(a, b) for a, b in zip(points, points[1:])) / length
            measured = True
            break
    if not measured:
        if kind == "pendulum" and links:
            S = math.dist(links[0]["a"]["point"], bodies[0]["anchor"])
        elif kind in {"incline_block", "incline_pulley"}:
            sf = next(s for s in scene["surfaces"] if s["type"] == "incline")
            S = math.dist(sf["polyline"][0], sf["polyline"][-1]) / 3
        elif kind == "projectile":
            S = scene["image"]["width"] * 0.75 / (20**2 / 9.81)
    scene["frame"]["px_per_m"] = value(
        max(1e-6, S),
        "px/m",
        0.8 if measured else 0.0,
        "geometry" if measured else "prior",
        "given" if measured else "assumed",
    )

    def physical(n, u):
        return value(
            n,
            u,
            0.8 if measured else 0.0,
            "geometry" if measured else "prior",
            "given" if measured else "assumed",
        )

    for body in bodies:
        body["initial"]["position"] = {
            "x": physical(body["anchor"][0] / S, "m"),
            "y": physical(body["anchor"][1] / S, "m"),
        }
        if body["type"] in {"ball", "bob"}:
            body["radius_m"] = physical((body["bbox"][2] - body["bbox"][0]) / 2 / S, "m")
    for sf in scene["surfaces"]:
        if sf["type"] == "incline":
            sf["length_m"] = physical(math.dist(sf["polyline"][0], sf["polyline"][-1]) / S, "m")

    def param(key, v):
        old = params.get(key)
        if not old or old["status"] == "assumed":
            params[key] = copy.deepcopy(v)

    if kind == "pendulum" and links:
        link = links[0]
        if link["b"]["ref"] == "pivot":
            link["a"], link["b"] = link["b"], link["a"]
            link["polyline"] = link["polyline"][::-1]
        pivot = link["a"]["point"]
        b = bodies[0]
        dx, dy = np.array(b["anchor"]) - np.array(pivot)
        link["length_m"] = link["length_m"] or physical(math.hypot(dx, dy) / S, "m")
        link["damping"] = value(0.0, "1/s", 0.0, "prior", "assumed")
        param("release_angle", value(math.degrees(math.atan2(dx, dy)), "deg"))
        param("angular_speed", zero("rad/s"))
        b["initial"]["position"] = {"x": physical(dx / S, "m"), "y": physical(dy / S, "m")}
    if kind in {"incline_block", "incline_pulley"}:
        sf = next(s for s in scene["surfaces"] if s["type"] == "incline")
        supported = next((b for b in bodies if b["on_surface"] == sf["id"]), bodies[0])
        bodies.sort(key=lambda b: b["id"] != supported["id"])
        origin = np.array(sf["polyline"][0])
        u = np.array(sf["polyline"][-1]) - origin
        u /= np.linalg.norm(u)
        param(
            "start_position", physical(float((np.array(supported["anchor"]) - origin) @ u) / S, "m")
        )
        param("initial_speed", assumed("initial_speed"))
        param("applied_force", zero("N"))
    if kind == "spring_mass" and links:
        link = links[0]
        b = bodies[0]
        if link["a"]["ref"] == b["id"]:
            link["a"], link["b"] = link["b"], link["a"]
            link["polyline"] = link["polyline"][::-1]
        vertical = abs(link["b"]["point"][1] - link["a"]["point"][1]) > abs(
            link["b"]["point"][0] - link["a"]["point"][0]
        )
        param("vertical", value(int(vertical), "1"))
        half = (b["bbox"][3] - b["bbox"][1]) / 2 if vertical else (b["bbox"][2] - b["bbox"][0]) / 2
        gap = (
            b["anchor"][1] - link["a"]["point"][1]
            if vertical
            else b["anchor"][0] - link["a"]["point"][0]
        ) - half
        if gap <= 0:
            warning(scene, "unsupported_spring_orientation", link["id"])
            scene["archetype"] = "unsupported"
        param("initial_stretch", physical(gap / S - link["rest_length_m"]["number"], "m"))
        param("initial_speed", assumed("initial_speed"))
        # The v1 spring solver models an ideal frictionless guide, not a contact.
        for body in bodies:
            body["on_surface"] = None
    if kind == "projectile":
        bodies[0]["on_surface"] = None  # the launch surface is not a continuing constraint
        arrow = next((a for a in scene["annotations"] if a["id"].startswith("velocity")), None)
        if arrow:
            points = arrow["geometry"]["points"]
            dx, dy = np.array(points[-1]) - np.array(points[0])
            param("launch_angle", value(math.degrees(math.atan2(-dy, dx)), "deg"))
        else:
            fit = next((v for k, v in evidence.items() if k.startswith("trajectory")), None)
            if fit:
                param("launch_angle", value(fit["angle_deg"], "deg", fit["confidence"]))
        speed = next((r for r in assignments if r["accepted"] and r["kind"] == "speed"), None)
        param(
            "launch_speed",
            value(speed["number"], "m/s", speed["confidence"], "ocr")
            if speed
            else assumed("launch_speed"),
        )
        ground = max(s["polyline"][0][1] for s in scene["surfaces"] if s["type"] == "floor")
        radius = (bodies[0]["bbox"][3] - bodies[0]["bbox"][1]) / 2
        param(
            "launch_height", physical(max(0.0, ground - bodies[0]["anchor"][1] - radius) / S, "m")
        )
        bodies[0]["initial"]["position"]["y"] = physical(-params["launch_height"]["number"], "m")
        bodies[0]["initial"]["position"]["x"] = physical(0.0, "m")
    if kind in {"atwood", "table_pulley", "incline_pulley"}:
        param("initial_speed", assumed("initial_speed"))
    if kind == "table_pulley":
        bodies.sort(key=lambda b: not bool(b["on_surface"]))
    if kind == "collision_1d":
        param("restitution", assumed("restitution"))
        bodies.sort(key=lambda b: b["anchor"][0])
    bindings = []

    def bind(id_, path, category, low, high, unit, handle=None):
        bindings.append(
            dict(
                id=id_,
                path=path,
                **{"class": category},
                control=dict(
                    min=float(low),
                    max=float(high),
                    step=0.01,
                    unit=unit,
                    locked=category == "geometry",
                ),
                labels=[a["id"] for a in scene["annotations"] if a.get("bound_to") == path],
                handle=handle,
            )
        )

    for b in bodies:
        bind(
            "mass_" + b["id"],
            f"bodies.{b['id']}.mass",
            "physics",
            0.01,
            max(100, b["mass"]["number"] * 2),
            "kg",
        )
    bind("g", "constants.g", "physics", 0.1, 30, "m/s^2")
    for key, v in params.items():
        if key.startswith("unplaced_") or key == "vertical":
            continue
        lo, hi = {
            "release_angle": (-80, 80),
            "angular_speed": (-10, 10),
            "launch_angle": (0, 85),
            "restitution": (0, 1),
            "initial_speed": (-30, 30),
            "applied_force": (-100, 100),
        }.get(key, (-10, 50))
        if v["number"] is not None:
            lo = min(lo, v["number"])
            hi = max(hi, v["number"])
        bind(
            key,
            "params." + key,
            "initial" if key not in {"restitution", "applied_force"} else "physics",
            lo,
            hi,
            v["unit"],
            {
                "release_angle": "bob",
                "start_position": "block",
                "initial_stretch": "spring_end",
                "launch_angle": "launch",
                "launch_speed": "launch",
            }.get(key),
        )
    for sf in scene["surfaces"]:
        if sf["type"] == "incline":
            bind(
                "theta_" + sf["id"],
                f"surfaces.{sf['id']}.angle_deg",
                "geometry",
                1,
                89,
                "deg",
                "incline_tip",
            )
            bind(
                "length_" + sf["id"],
                f"surfaces.{sf['id']}.length_m",
                "geometry",
                0.1,
                max(10, sf["length_m"]["number"] * 2),
                "m",
            )
        if any(b["on_surface"] == sf["id"] for b in bodies):
            for name in ("mu_s", "mu_k"):
                bind(name + "_" + sf["id"], f"surfaces.{sf['id']}.{name}", "physics", 0, 2, "1")
    for link in links:
        if kind == "pendulum":
            bind(
                "pendulum_length",
                f"links.{link['id']}.length_m",
                "initial",
                0.1,
                max(3, link["length_m"]["number"] * 2),
                "m",
            )
        if link["type"] == "spring":
            bind("k_" + link["id"], f"links.{link['id']}.k", "physics", 1, 1000, "N/m")
        if link["damping"]:
            bind(
                "damping_" + link["id"],
                f"links.{link['id']}.damping",
                "physics",
                0,
                30,
                link["damping"]["unit"],
            )
    if kind == "collision_1d":
        for b in bodies:
            bind("v_" + b["id"], f"bodies.{b['id']}.initial.velocity.x", "initial", -30, 30, "m/s")
    scene["bindings"] = bindings
    scene["repairs"] = sprites.repairs(bodies, scene["surfaces"])
    return scene
