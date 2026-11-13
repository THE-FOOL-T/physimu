"""Structural rules for v1. No physics solver lives in the backend."""


def match(scene):
    bodies = scene["bodies"]
    links = scene["links"]
    pulleys = scene["pulleys"]
    surfaces = {s["id"]: s for s in scene["surfaces"]}
    annotations = scene["annotations"]
    if not bodies:
        return "unsupported", 0.0, "No supported moving body was measured."
    if any(b["type"] not in {"block", "ball", "bob", "cart"} for b in bodies):
        return "unsupported", 0.0, "An unknown moving object needs manual classification."
    if (
        len(bodies) == 1
        and bodies[0]["type"] == "bob"
        and len(links) == 1
        and not pulleys
        and any(a["id"] == "pivot" for a in annotations)
        and any(
            link["type"] in {"rope", "rod"}
            and {link["a"]["ref"], link["b"]["ref"]} == {"pivot", bodies[0]["id"]}
            for link in links
        )
    ):
        return "pendulum", 0.9, None
    if len(bodies) == 1 and len(links) == 1 and links[0]["type"] == "spring":
        return "spring_mass", 0.9, None
    if (
        len(bodies) == 2
        and len(pulleys) == 1
        and any(
            link["type"] == "rope"
            and {link["a"]["ref"], link["b"]["ref"]} == {b["id"] for b in bodies}
            for link in links
        )
    ):
        supported = [b for b in bodies if b.get("on_surface")]
        if any(surfaces[b["on_surface"]]["type"] == "incline" for b in supported):
            return "incline_pulley", 0.9, None
        if len(supported) == 1:
            return "table_pulley", 0.85, None
        if not supported:
            return "atwood", 0.85, None
    if len(bodies) == 1 and not pulleys and not links and bodies[0].get("on_surface"):
        if surfaces[bodies[0]["on_surface"]]["type"] == "incline":
            return "incline_block", 0.9, None
    if (
        len(bodies) == 2
        and not links
        and not pulleys
        and bodies[0].get("on_surface")
        and bodies[0]["on_surface"] == bodies[1].get("on_surface")
    ):
        return "collision_1d", 0.85, None
    if (
        len(bodies) == 1
        and bodies[0]["type"] == "ball"
        and not links
        and not pulleys
        and any(a["id"].startswith(("velocity", "trajectory", "launch")) for a in annotations)
        and any(s["type"] == "floor" for s in surfaces.values())
    ):
        return "projectile", 0.85, None
    return (
        "unsupported",
        0.0,
        "Detected objects and attachments do not match a supported mechanics archetype.",
    )
