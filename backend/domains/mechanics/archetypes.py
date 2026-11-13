"""Rank solver capabilities using measured topology and explicit contradictions."""


def hypotheses(scene):
    bodies, links, pulleys = (scene[k] for k in ("bodies", "links", "pulleys"))
    surfaces = {s["id"]: s for s in scene["surfaces"]}
    ids = {b["id"] for b in bodies}
    supported = [b for b in bodies if b.get("on_surface") in surfaces]
    ropes = [
        link
        for link in links
        if link["type"] == "rope" and {link["a"]["ref"], link["b"]["ref"]} == ids
    ]
    active = [link for link in links if link["a"]["ref"] in ids or link["b"]["ref"] in ids]
    rows = []

    def candidate(kind, requirements):
        good = [description for passed, description in requirements if passed]
        bad = [description for passed, description in requirements if not passed]
        rows.append(
            dict(
                archetype=kind,
                confidence=0.9 if not bad else max(0.0, 0.5 - 0.15 * len(bad)),
                supporting=good,
                contradictions=bad,
                score=float(10 * len(bad) - len(good)),
            )
        )

    known = all(b["type"] in {"block", "ball", "bob", "cart"} for b in bodies)
    single = [
        (len(bodies) == 1, "solver supports one moving body"),
        (known, "moving body types are supported"),
    ]
    pair = [
        (len(bodies) == 2, "solver supports two moving bodies"),
        (known, "moving body types are supported"),
    ]
    pendulum_links = [
        link
        for link in active
        if link["type"] in {"rope", "rod"} and "pivot" in {link["a"]["ref"], link["b"]["ref"]}
    ]
    candidate(
        "pendulum",
        single
        + [
            (any(b["type"] == "bob" for b in bodies), "a pendulum bob was measured"),
            (len(pendulum_links) == 1, "one measured link connects bob and fixed pivot"),
            (len(active) == 1 and not pulleys, "no additional device constrains the bob"),
        ],
    )
    candidate(
        "spring_mass",
        single
        + [
            (
                len([link for link in active if link["type"] == "spring"]) == 1,
                "one spring connects the moving body",
            ),
            (len(active) == 1 and not pulleys, "no additional device constrains the spring mass"),
        ],
    )
    pulley_common = pair + [
        (len(pulleys) == 1, "one fixed pulley was measured"),
        (len(ropes) == 1, "one rope connects both bodies"),
        (len(active) == 1, "both bodies share one mechanical link"),
    ]
    candidate("atwood", pulley_common + [(not supported, "both rope-connected masses are hanging")])
    candidate(
        "table_pulley",
        pulley_common
        + [
            (
                len(supported) == 1 and surfaces[supported[0]["on_surface"]]["type"] == "floor",
                "one body contacts a horizontal table and the other hangs",
            )
        ],
    )
    candidate(
        "incline_pulley",
        pulley_common
        + [
            (
                len(supported) == 1 and surfaces[supported[0]["on_surface"]]["type"] == "incline",
                "one body contacts an incline and the other hangs",
            )
        ],
    )
    candidate(
        "incline_block",
        single
        + [
            (
                len(supported) == 1 and surfaces[supported[0]["on_surface"]]["type"] == "incline",
                "the moving body contacts an incline",
            ),
            (not active and not pulleys, "no rope spring or pulley constrains the block"),
        ],
    )
    candidate(
        "collision_1d",
        pair
        + [
            (
                len(supported) == 2
                and supported[0]["on_surface"] == supported[1]["on_surface"]
                and surfaces[supported[0]["on_surface"]]["type"] == "floor",
                "both bodies contact the same horizontal surface",
            ),
            (not active and not pulleys, "the bodies move without mechanical links"),
        ],
    )
    candidate(
        "projectile",
        single
        + [
            (any(b["type"] == "ball" for b in bodies), "a projectile body was measured"),
            (
                any(
                    a["id"].startswith(("velocity", "trajectory", "launch"))
                    for a in scene["annotations"]
                ),
                "a launch vector or trajectory was measured",
            ),
            (
                any(s["type"] == "floor" for s in surfaces.values()),
                "a landing reference was measured",
            ),
            (not active and not pulleys, "the projectile has no mechanical link"),
        ],
    )
    return sorted(rows, key=lambda r: (r["score"], r["archetype"]))


def match(scene):
    rows = hypotheses(scene)
    valid = [r for r in rows if not r["contradictions"]]
    if len(valid) == 1:
        return valid[0]["archetype"], valid[0]["confidence"], None
    if len(valid) > 1:
        return (
            "unsupported",
            0.0,
            "Several physical interpretations remain plausible; review the measured contacts and links.",
        )
    return (
        "unsupported",
        0.0,
        "Detected objects and attachments do not match a supported mechanics archetype. "
        + "; ".join(rows[0]["contradictions"]),
    )
