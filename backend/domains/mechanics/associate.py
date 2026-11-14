"""Typed, global label assignment. Rejections stay visible as unplaced Values."""

import math
import numpy as np
from scipy.optimize import linear_sum_assignment


def centre(box):
    return [(box[0] + box[2]) / 2, (box[1] + box[3]) / 2]


def distance(point, points):
    best = float("inf")
    if len(points) == 1:
        return math.dist(point, points[0])
    for a, b in zip(points, points[1:]):
        a, b, p = np.array(a), np.array(b), np.array(point)
        d = b - a
        t = float(np.clip((p - a) @ d / max(1e-9, d @ d), 0, 1))
        best = min(best, float(np.linalg.norm(p - (a + t * d))))
    return best


def val(token, confidence):
    return dict(
        number=token.number,
        unit=token.unit,
        status="given",
        source=token.source if token.source in {"ocr", "vlm"} else "ocr",
        confidence=float(confidence),
    )


def put(scene, path, value):
    target = scene
    bits = path.split(".")
    for bit in bits[:-1]:
        target = (
            next(x for x in target if x["id"] == bit) if isinstance(target, list) else target[bit]
        )
    old = target.get(bits[-1])
    if old and (old.get("source") == "user" or old.get("status") == "user"):
        return False
    target[bits[-1]] = value
    return True


def targets(scene):
    result = []

    def add(kind, path, ref, points, confidence=0.9):
        result.append(dict(kind=kind, path=path, ref=ref, points=points, confidence=confidence))

    for body in scene["bodies"]:
        for kind, field in [("mass", "mass"), ("speed", "initial.velocity.x"), ("name", None)]:
            points = [body["anchor"]]
            if kind == "speed":
                for arrow in scene["annotations"]:
                    route = arrow.get("geometry", {}).get("points", [])
                    if not arrow["id"].startswith("velocity") or len(route) < 2:
                        continue
                    owners = sorted(scene["bodies"], key=lambda b: math.dist(route[0], b["anchor"]))
                    if (
                        owners[0]["id"] == body["id"]
                        and math.dist(route[0], body["anchor"]) <= 120
                        and (
                            len(owners) == 1
                            or math.dist(route[0], owners[1]["anchor"])
                            - math.dist(route[0], owners[0]["anchor"])
                            > 12
                        )
                    ):
                        points.extend(route)
            add(
                kind,
                f"bodies.{body['id']}.{field}" if field else None,
                body["id"],
                points,
            )
    for surface in scene["surfaces"]:
        for kind, field in [("friction_static", "mu_s"), ("friction_kinetic", "mu_k")]:
            add(kind, f"surfaces.{surface['id']}.{field}", surface["id"], surface["polyline"])
        if surface["type"] == "incline":
            add(
                "angle",
                f"surfaces.{surface['id']}.angle_deg",
                surface["id"],
                [surface["polyline"][0]],
            )
    for link in scene["links"]:
        routes = list(link["polyline"])
        for annotation in scene["annotations"]:
            geometry = annotation["geometry"]
            if annotation["id"].startswith(f"alternate_state_{link['id']}_"):
                routes.extend(geometry["points"])
        add("length", f"links.{link['id']}.length_m", link["id"], routes)
        if link["type"] == "spring":
            add("spring_constant", f"links.{link['id']}.k", link["id"], link["polyline"])
            add("damping", f"links.{link['id']}.damping", link["id"], link["polyline"])
    pivot = next((a for a in scene["annotations"] if a["id"] == "pivot"), None)
    if pivot:
        add("angle", "params.release_angle", "pivot", pivot["geometry"]["points"])
        for link in scene["links"]:
            if link["type"] in {"rope", "rod"}:
                add("damping", f"links.{link['id']}.damping", link["id"], link["polyline"])
    if len(scene["bodies"]) == 1 and scene["bodies"][0]["type"] == "ball" and not scene["links"]:
        add(
            "angle", "params.launch_angle", scene["bodies"][0]["id"], [scene["bodies"][0]["anchor"]]
        )
    for annotation in scene["annotations"]:
        if annotation["type"] == "dimension":
            add("length", None, annotation["id"], annotation["geometry"]["points"])
    for force in scene["forces"]:
        add("force", f"forces.{force['id']}.magnitude", force["id"], [force["tail"], force["head"]])
    add("gravity", "constants.g", None, [])
    add("restitution", "params.restitution", None, [])
    add("angular_speed", "params.angular_speed", None, [])
    return result


def associate(scene, tokens, detection_confidences=None):
    possible = targets(scene)
    pivot = any(a["id"] == "pivot" for a in scene["annotations"])
    # A nearby bare m/M/g is a body name. A numeric label still needs its unit;
    # numeric strings without one remain unplaced rather than guessing metres.
    names = [t for t in tokens if t.kind == "name"]
    named_owners = {}
    for token in names:
        if scene["bodies"]:
            body = min(scene["bodies"], key=lambda b: math.dist(centre(token.bbox), b["anchor"]))
            if math.dist(centre(token.bbox), body["anchor"]) <= 120:
                named_owners[token.name.lower()] = body["id"]
    matrix = np.full((len(tokens), len(possible) + len(tokens)), 1e6)
    for i, token in enumerate(tokens):
        matrix[i, len(possible) + i] = 1.1
        if token.conflict:
            continue
        for j, target in enumerate(possible):
            if token.kind != target["kind"]:
                continue
            if token.kind == "damping" and token.unit != ("1/s" if pivot else "kg/s"):
                continue
            dist = distance(centre(token.bbox), target["points"]) if target["points"] else 0.0
            reach = 120.0
            if (
                pivot
                and len(scene["links"]) == 1
                and (
                    token.kind == "angle"
                    and target["path"] == "params.release_angle"
                    or token.kind == "length"
                    and target["ref"] == scene["links"][0]["id"]
                )
            ):
                link = scene["links"][0]
                reach = max(
                    reach, min(300.0, math.dist(link["a"]["point"], link["b"]["point"]) * 0.5)
                )
            if dist > reach:
                continue
            named = named_owners.get((token.name or "").lower())
            if named and token.kind in {"mass", "speed"} and named != target["ref"]:
                continue
            matrix[i, j] = dist / reach + (1 - token.confidence) * 0.2
    report = []
    if not tokens:
        return report
    rows, cols = linear_sum_assignment(matrix)
    for i, j in zip(rows, cols):
        token = tokens[i]
        row = {
            **token.as_dict(),
            "ref": None,
            "path": None,
            "accepted": False,
            "reason": "conflicting_readings" if token.conflict else "no_plausible_owner",
        }
        plausible = sorted(v for v in matrix[i, : len(possible)] if v < 1.1)
        ambiguous = (
            token.kind in {"mass", "speed"}
            and not named_owners.get((token.name or "").lower())
            and len(plausible) > 1
            and plausible[1] - plausible[0] < 0.1
        )
        if ambiguous:
            row["reason"] = "ambiguous_owner"
        if not ambiguous and j < len(possible) and matrix[i, j] < 1.1:
            target = possible[j]
            confidence = min(
                token.confidence, float((detection_confidences or {}).get(target["ref"], 0.9))
            ) * (1 - 0.4 * matrix[i, j])
            row.update(
                ref=target["ref"],
                path=target["path"],
                accepted=True,
                reason="typed_assignment",
                confidence=confidence,
            )
            if token.kind == "name":
                scene["annotations"].append(
                    dict(
                        id="name_" + target["ref"],
                        type="label",
                        geometry=dict(text=token.name),
                        bound_to=None,
                    )
                )
            elif target["path"]:
                old = None
                if token.kind == "angle":
                    old = next((s for s in scene["surfaces"] if s["id"] == target["ref"]), {}).get(
                        "angle_deg"
                    )
                if not put(scene, target["path"], val(token, confidence)):
                    row.update(accepted=False, reason="user_value_preserved")
                elif old and old["number"] is not None and abs(old["number"] - token.number) > 5:
                    scene["warnings"].append(
                        dict(
                            code="angle_mismatch",
                            ref=target["ref"],
                            message_key="mech.angle_mismatch",
                        )
                    )
                if token.kind == "friction_kinetic" and token.name in {"μ", "mu"}:
                    interpreted = {**val(token, confidence * 0.7), "status": "assumed"}
                    put(scene, target["path"], interpreted.copy())
                    put(scene, target["path"].replace("mu_k", "mu_s"), interpreted.copy())
                    scene["warnings"].append(
                        dict(
                            code="friction_interpretation_assumed",
                            ref=target["ref"],
                            message_key="mech.friction_interpretation_assumed",
                        )
                    )
        if not row["accepted"] and token.number is not None:
            key = f"unplaced_{len(scene['params']) + 1}"
            scene["params"][key] = val(token, token.confidence)
            row["unplaced_path"] = "params." + key
        report.append(row)
    return report
