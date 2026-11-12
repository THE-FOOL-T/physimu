"""Explicit assumed priors; these are not measurements or recognition results."""

import copy
import math

DEFAULTS = {
    "mass": (1.0, "kg"),
    "g": (9.81, "m/s^2"),
    "mu": (0.0, "1"),
    "damping": (0.0, "kg/s"),
    "restitution": (1.0, "1"),
    "launch_speed": (20.0, "m/s"),
    "incline_length": (3.0, "m"),
    "pendulum_length": (1.0, "m"),
    "spring_rest_length": (0.5, "m"),
}


def assumed(name: str) -> dict:
    number, unit = DEFAULTS[name]
    return dict(number=number, unit=unit, status="assumed", source="prior", confidence=0.0)


def scene_defaults(document: dict) -> dict:
    """Fill absent keys only. Explicit nulls remain unresolved for the solver."""
    scene = copy.deepcopy(document)
    archetype = scene.get("archetype")
    params = scene.setdefault("params", {})
    if archetype == "projectile":
        params.setdefault("launch_speed", assumed("launch_speed"))
    if archetype == "collision_1d":
        params.setdefault("restitution", assumed("restitution"))
    for surface in scene.get("surfaces", []):
        if surface.get("type") == "incline":
            surface.setdefault("length_m", assumed("incline_length"))
    for link in scene.get("links", []):
        if link.get("type") == "spring":
            link.setdefault("rest_length_m", assumed("spring_rest_length"))
            link.setdefault("damping", assumed("damping"))
        if archetype == "pendulum" and link.get("type") in ("rod", "rope"):
            link.setdefault("length_m", assumed("pendulum_length"))
            link.setdefault(
                "damping",
                dict(number=0.0, unit="1/s", status="assumed", source="prior", confidence=0.0),
            )
    frame = scene.get("frame", {})
    if "px_per_m" not in frame:
        scale = 100.0  # Other diagrams require a printed dimension for a real scale.
        if archetype == "projectile":
            scale = scene.get("image", {}).get("width", 800) * 0.75 / (20**2 / 9.81)
        if archetype in ("incline_block", "incline_pulley"):
            incline = next(
                (s for s in scene.get("surfaces", []) if s.get("type") == "incline"), None
            )
            if incline and len(incline.get("polyline", [])) >= 2:
                scale = math.dist(incline["polyline"][0], incline["polyline"][-1]) / 3
        if archetype == "pendulum" and scene.get("links"):
            link = scene["links"][0]
            scale = math.dist(link["a"]["point"], link["b"]["point"])
        frame["px_per_m"] = dict(
            number=scale, unit="px/m", status="assumed", source="prior", confidence=0.0
        )
        scene["frame"] = frame
    return scene
