"""Physics plausibility, alternative scoring and provenance; never numerical simulation."""

import copy
import itertools
import math

import numpy as np

from .associate import distance
from .archetypes import match


def warning(scene, code, ref=None):
    if not any(w["code"] == code and w["ref"] == ref for w in scene["warnings"]):
        scene["warnings"].append(dict(code=code, ref=ref, message_key="mech." + code))


def surface_options(body, surfaces):
    # A measured contact within the 12px gate outranks an unattached reading.
    # This also keeps a partly masked incline body from becoming an Atwood bob.
    options = [(None, 12.5)]
    for sf in surfaces:
        if sf["type"] not in {"floor", "incline"}:
            continue
        error = min(distance(p, sf["polyline"]) for p in body["mask"])
        if error <= 12:
            options.append((sf["id"], error))
    return sorted(options, key=lambda x: x[1])[:3]


def violations(scene):
    errors = []
    for name, v in scene["params"].items():
        if not name.startswith("unplaced_") and v["number"] is None:
            errors.append(("unresolved_parameter", None))
    if scene["archetype"] == "projectile":
        for name, minimum, maximum in [
            ("launch_speed", 0, float("inf")),
            ("launch_height", 0, float("inf")),
            ("launch_angle", 0, 90),
        ]:
            v = scene["params"].get(name)
            if v and (v["number"] is None or not minimum <= v["number"] <= maximum):
                errors.append(("invalid_launch", None))
    for b in scene["bodies"]:
        if b["mass"]["number"] is None or b["mass"]["number"] <= 0:
            errors.append(("invalid_mass", b["id"]))
    if scene["constants"]["g"]["number"] is None or scene["constants"]["g"]["number"] <= 0:
        errors.append(("invalid_gravity", None))
    for sf in scene["surfaces"]:
        if (
            sf["type"] == "incline"
            and sf.get("angle_deg")
            and (sf["angle_deg"]["number"] is None or not 0 < sf["angle_deg"]["number"] < 90)
        ):
            errors.append(("unsupported_incline_orientation", sf["id"]))
        if (
            any(sf[k]["number"] is None for k in ("mu_s", "mu_k"))
            or sf["mu_k"]["number"] < 0
            or sf["mu_s"]["number"] < sf["mu_k"]["number"]
        ):
            errors.append(("invalid_friction", sf["id"]))
    objects = {
        o["id"]: o
        for group in (scene["bodies"], scene["pulleys"], scene["annotations"], scene["surfaces"])
        for o in group
    }
    for link in scene["links"]:
        for field in ("length_m", "rest_length_m", "k"):
            value = link.get(field)
            if value and (value["number"] is None or value["number"] <= 0):
                errors.append(("invalid_link_value", link["id"]))
        damping = link.get("damping")
        if damping and (damping["number"] is None or damping["number"] < 0):
            errors.append(("invalid_link_value", link["id"]))
        if link["a"]["ref"] == link["b"]["ref"]:
            errors.append(("attachment_invalid", link["id"]))
        for end in ("a", "b"):
            endpoint = link[end]
            obj = objects.get(endpoint["ref"])
            if obj is None:
                errors.append(("attachment_invalid", link["id"]))
                continue
            if "anchor" in obj:
                reach = max(
                    12.0,
                    math.hypot(obj["bbox"][2] - obj["bbox"][0], obj["bbox"][3] - obj["bbox"][1])
                    * 0.65,
                )
                if math.dist(endpoint["point"], obj["anchor"]) > reach:
                    errors.append(("attachment_unreached", link["id"]))
        if link["type"] == "rope":
            for pulley in scene["pulleys"]:
                pts = np.array(link["polyline"])
                delta = np.abs(
                    np.linalg.norm(pts - np.array(pulley["center"]), axis=1) - pulley["radius_px"]
                )
                if float(delta.min()) > max(8, pulley["radius_px"] * 0.25):
                    errors.append(("rope_route_invalid", link["id"]))
    restitution = scene["params"].get("restitution")
    if restitution and (restitution["number"] is None or not 0 <= restitution["number"] <= 1):
        errors.append(("invalid_restitution", None))
    for force in scene["forces"]:
        # Current archetypes have scalar solvers for specific force arrangements.
        # Preserve an arbitrary drawn force but require editing before simulation.
        if not force.get("magnitude") or force["magnitude"]["number"] != 0:
            errors.append(("unsupported_applied_force", force["id"]))
    return errors


def interpretations(scene, link_choices):
    surface_choices = [surface_options(b, scene["surfaces"]) for b in scene["bodies"]]
    alternatives = []
    choices = [[(ref, error) for ref, error in entries] for entries in surface_choices]
    combinations = itertools.product(*choices) if choices else [()]
    best = None
    for selection in itertools.islice(combinations, 64):
        base = copy.deepcopy(scene)
        for b, (ref, _) in zip(base["bodies"], selection):
            b["on_surface"] = ref
        assignments = [
            link_choices.get(link["id"], [(link["a"]["ref"], link["b"]["ref"], 0.0)])
            for link in base["links"]
        ]
        for endpoints in itertools.islice(itertools.product(*assignments), 16):
            candidate = copy.deepcopy(base)
            for link, (a, b, _) in zip(candidate["links"], endpoints):
                link["a"]["ref"], link["b"]["ref"] = a, b
            kind, confidence, reason = match(candidate)
            candidate["archetype"] = kind
            errors = violations(candidate)
            cost = (
                100 * len(errors)
                + (50 if kind == "unsupported" else 0)
                + sum(err for _, err in selection)
                + sum(v[2] for v in endpoints)
            )
            record = dict(
                archetype=kind,
                score=float(cost),
                violations=[e[0] for e in errors],
                surfaces={b["id"]: b["on_surface"] for b in candidate["bodies"]},
                attachments={
                    link["id"]: [link["a"]["ref"], link["b"]["ref"]] for link in candidate["links"]
                },
            )
            alternatives.append(record)
            if best is None or cost < best[0]:
                best = (cost, candidate, reason, confidence)
    ranked = sorted(alternatives, key=lambda r: r["score"])[:16]
    if best and any(
        r["archetype"] != best[1]["archetype"]
        and r["archetype"] != "unsupported"
        and not r["violations"]
        and r["score"] - best[0] <= 3
        for r in ranked
    ):
        warning(best[1], "ambiguous_interpretation")
    return best[1:] if best else (scene, "No objects available", 0.0), ranked


def finalize(scene, reason=None):
    errors = violations(scene)
    for code, ref in errors:
        warning(scene, code, ref)
    if errors:
        # Retain the recognized arrangement (including its unit conventions) so
        # editing a bad mass/attachment can repair it without rebuilding objects.
        scene["meta"]["provenance"] = "unsupported"
        return "Measured scene violates a required physical or attachment constraint."
    if scene["archetype"] == "incline_block":
        sf = next(s for s in scene["surfaces"] if s["type"] == "incline")
        if any(sf[k]["status"] == "assumed" for k in ("mu_s", "mu_k")):
            warning(scene, "assumed_regime", sf["id"])
        ratio = math.tan(math.radians(sf["angle_deg"]["number"]))
        warning(scene, "regime_slide" if ratio > sf["mu_s"]["number"] else "regime_stick", sf["id"])
    if scene["archetype"] in {"atwood", "table_pulley", "incline_pulley"} and any(
        b["mass"]["status"] == "assumed" for b in scene["bodies"]
    ):
        warning(scene, "assumed_regime")
    if scene["archetype"] == "unsupported":
        scene["meta"]["provenance"] = "unsupported"
        return reason or "No supported physical interpretation was established."

    def assumed(v):
        if isinstance(v, dict):
            if "number" in v and (v.get("status") == "assumed" or v["number"] is None):
                return True
            return any(assumed(x) for x in v.values())
        return isinstance(v, list) and any(assumed(x) for x in v)

    incomplete = assumed(scene) or any(
        w["code"] not in {"regime_stick", "regime_slide"} for w in scene["warnings"]
    )
    scene["meta"]["provenance"] = "partial" if incomplete else "extracted"
    return None
