"""Ownership regressions exercise production compilation, never fixture substitution."""

import copy

import pytest

from circuit_sim.backend.domains.mechanics.associate import associate
from circuit_sim.backend.domains.mechanics.labels import parse
from circuit_sim.backend.domains.mechanics.perception import calibrate
from circuit_sim.backend.domains.mechanics.scene import Scene
from circuit_sim.backend.tests.mechanics.perception_fixtures import case
from circuit_sim.backend.domains.mechanics.engine import analyze_mechanics_page
from circuit_sim.backend.tools.mechanics.build_fixtures import fixtures


def measured_fixture(name):
    s = fixtures()[name].model_dump(mode="json", by_alias=True)

    def priors(v):
        if isinstance(v, dict):
            if "number" in v:
                v.update(status="assumed", source="prior", confidence=0.0)
            else:
                for item in v.values():
                    priors(item)
        elif isinstance(v, list):
            for item in v:
                priors(item)

    priors(s)
    return s


@pytest.mark.parametrize(
    "name,path",
    [
        ("projectile_ground", "params.launch_speed"),
        ("incline", "params.initial_speed"),
        ("spring_horizontal", "params.initial_speed"),
        ("spring_vertical", "params.initial_speed"),
        ("atwood", "params.initial_speed"),
        ("table_pulley", "params.initial_speed"),
        ("incline_pulley", "params.initial_speed"),
        ("collision", "bodies.B1.initial.velocity.x"),
    ],
)
def test_speed_assignment_and_annotation_follow_solver_owner(name, path):
    s = measured_fixture(name)
    b = s["bodies"][0]
    s["annotations"].append(
        dict(
            id="observed_speed",
            type="label",
            geometry=dict(text="v0=7 m/s"),
            bound_to=f"bodies.{b['id']}.initial.velocity.x",
        )
    )
    rows = associate(s, parse("v0=7 m/s", b["bbox"]))
    calibrate(s, rows, {})
    assert rows[0]["path"] == path
    assert s["annotations"][-1]["bound_to"] == path
    binding = next(v for v in s["bindings"] if v["path"] == path)
    assert "observed_speed" in binding["labels"]
    canonical = Scene.model_validate(s)
    from circuit_sim.backend.domains.mechanics.scene import resolve_path

    value = resolve_path(canonical, path)
    assert value.number == 7
    assert value.status == "given" and value.source == "ocr"


def test_launch_angle_is_measured_by_ocr_and_keeps_its_binding():
    image, _, detect, reader = case("projectile_ground")

    def text(*args, **kwargs):
        rows, notes = reader(*args, **kwargs)
        rows.append(dict(text="θ=32°", bbox=[60.0, 370.0, 115.0, 390.0], confidence=0.96))
        return rows, notes

    result = analyze_mechanics_page(image, {"style": "printed"}, detector=detect, text_reader=text)
    s = result["scene"]
    assert s["archetype"] == "projectile"
    assert s["params"]["launch_angle"]["number"] == 32
    assert s["params"]["launch_angle"]["source"] == "ocr"
    a = next(a for a in s["annotations"] if a["geometry"]["text"] == "θ=32°")
    assert a["bound_to"] == "params.launch_angle"


def test_user_launch_speed_survives_compilation_and_unrelated_measurements():
    s = measured_fixture("projectile_ground")
    s["params"]["launch_speed"].update(number=9.0, status="user", source="user", confidence=1.0)
    before = copy.deepcopy(s["params"]["launch_speed"])
    rows = associate(s, parse("20 m/s", s["bodies"][0]["bbox"]))
    calibrate(s, rows, {})
    assert s["params"]["launch_speed"] == before
    assert not rows[0]["accepted"] and rows[0]["reason"] == "user_value_preserved"


def test_pendulum_damping_units_are_distinct_from_spring_damping():
    s = measured_fixture("pendulum")
    row = associate(s, parse("c=0.4 1/s", [300, 160, 330, 180]))[0]
    assert row["accepted"] and row["path"] == "links.L1.damping"
    calibrate(s, [row], {})
    assert Scene.model_validate(s).links[0].damping.number == 0.4


def test_subscript_friction_and_speed_label_near_owned_arrow_tip():
    assert parse("μₛ=0.4")[0].kind == "friction_static"
    s = measured_fixture("projectile_ground")
    body = s["bodies"][0]
    x, y = body["anchor"]
    s["annotations"].append(
        dict(id="velocity_long", type="axis", geometry=dict(points=[[x, y], [x + 250, y - 30]]))
    )
    row = associate(s, parse("v0=40 m/s", [x + 240, y - 45, x + 280, y - 20]))[0]
    assert row["accepted"] and row["ref"] == body["id"]
