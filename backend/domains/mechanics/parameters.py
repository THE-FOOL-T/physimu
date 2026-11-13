"""Compile observed quantities to the single Value path consumed by each solver.

Association happens before topology is resolved. Move ownership afterwards, keeping
the OCR report and annotations in sync rather than copying an unbound solver value.
"""

import copy
import math

from .associate import put


def compile_parameters(scene, assignments):
    kind = scene["archetype"]
    bodies = scene["bodies"]
    if not bodies:
        return
    supported = next((b for b in bodies if b.get("on_surface")), bodies[0])
    owners = {}
    for row in assignments:
        if not row["accepted"] or row["kind"] != "speed" or not row.get("path"):
            continue
        old_path = row["path"]
        body = next((b for b in bodies if b["id"] == row["ref"]), None)
        if not body:
            continue
        observed = copy.deepcopy(body["initial"]["velocity"]["x"])
        # A signed component owns its direction. An unsigned speed can use an
        # associated arrow; absence of an arrow never invents a negative sign.
        arrows = [
            a
            for a in scene["annotations"]
            if a["id"].startswith("velocity") and len(a["geometry"].get("points", [])) >= 2
        ]
        arrow = min(
            arrows,
            key=lambda a: math.dist(a["geometry"]["points"][0], body["anchor"]),
            default=None,
        )
        direction = None
        if arrow and math.dist(arrow["geometry"]["points"][0], body["anchor"]) <= 120:
            a, b = arrow["geometry"]["points"][0], arrow["geometry"]["points"][-1]
            direction = (b[0] - a[0], b[1] - a[1])
        path = old_path
        if kind == "projectile":
            path = "params.launch_speed"
        elif kind in {"incline_block", "spring_mass", "atwood", "table_pulley", "incline_pulley"}:
            path = "params.initial_speed"
        if observed["number"] >= 0 and direction:
            dx, dy = direction
            axis = dx
            if kind == "spring_mass" and scene["links"]:
                link = scene["links"][0]
                axis = (
                    dy
                    if abs(link["b"]["point"][1] - link["a"]["point"][1])
                    > abs(link["b"]["point"][0] - link["a"]["point"][0])
                    else dx
                )
            elif kind in {"atwood", "table_pulley", "incline_pulley"}:
                axis = dy if body != supported else -dy if kind == "atwood" else dx
            elif kind == "incline_block":
                sf = next(s for s in scene["surfaces"] if s["id"] == body["on_surface"])
                theta = math.radians(sf["angle_deg"]["number"])
                axis = dx * math.cos(theta) - dy * math.sin(theta)
            if kind != "projectile" and axis < 0:
                observed["number"] *= -1
        if not put(scene, path, observed):
            row.update(accepted=False, reason="user_value_preserved")
            continue
        if path in owners and owners[path]["number"] != observed["number"]:
            scene["params"][path.split(".")[-1]] = {
                **observed,
                "number": None,
                "status": "assumed",
                "confidence": 0.0,
            }
            owners[path].update(accepted=False, reason="conflicting_coupled_speeds")
            row.update(accepted=False, reason="conflicting_coupled_speeds")
            scene["warnings"].append(
                dict(
                    code="conflicting_coupled_speeds",
                    ref=None,
                    message_key="mech.conflicting_coupled_speeds",
                )
            )
        else:
            owners[path] = row
        row["path"] = path
        row["number"] = observed["number"]
        if old_path != path:
            for a in scene["annotations"]:
                if a.get("bound_to") == old_path:
                    a["bound_to"] = path
