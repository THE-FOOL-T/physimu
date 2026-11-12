"""Authored scene contract and deterministic painter, not extraction accuracy."""

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest
from pydantic import ValidationError

from circuit_sim.backend.domains.mechanics.scene import Scene
from circuit_sim.backend.tools.mechanics.build_fixtures import fixtures
from circuit_sim.backend.tools.mechanics.paint_scene import paint_scene, spring_points

ROOT = Path(__file__).resolve().parents[3]
NAMES = [
    "projectile_ground",
    "projectile_cliff",
    "incline",
    "pendulum",
    "spring_horizontal",
    "spring_vertical",
    "atwood",
    "table_pulley",
    "incline_pulley",
    "collision",
]


def raw(name="incline"):
    return json.loads((ROOT / "fixtures/mechanics" / f"{name}.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", NAMES)
def test_authored_fixtures_are_canonical_reproducible_and_paint_exactly(name):
    document = raw(name)
    scene = Scene.model_validate(document)
    assert scene.model_dump(mode="json", by_alias=True) == document
    assert fixtures()[name] == scene
    assert scene.meta.provenance == "authored"
    assert "SYNTHETIC / AUTHORED" in scene.annotations[0].geometry.text
    from PIL import Image

    with Image.open(ROOT / "fixtures/mechanics" / f"{name}.png") as image:
        assert image.size == (scene.image.width, scene.image.height)
        assert image.convert("RGB").tobytes() == paint_scene(scene).tobytes()
    assert (
        hashlib.sha256(paint_scene(scene).tobytes()).digest()
        == hashlib.sha256(paint_scene(scene).tobytes()).digest()
    )


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.update(extra=1),
        lambda d: d.update(version=True),
        lambda d: d.update(frame=None),
        lambda d: d["bodies"][0]["mass"].update(number=float("nan")),
        lambda d: d["bodies"][0]["mass"].update(number=float("inf")),
        lambda d: d["bodies"][0]["mass"].update(number="5"),
        lambda d: d["bodies"][0]["mass"].update(number=True),
        lambda d: d["bodies"][0]["mass"].update(unit="g"),
        lambda d: d["bodies"][0]["mass"].update(confidence=1.1),
        lambda d: d["image"].update(width=0),
        lambda d: d["bodies"][0].update(id="S1"),
        lambda d: d["bodies"][0].update(on_surface="missing"),
        lambda d: d["bindings"][0].update(path="params.missing"),
        lambda d: d["bindings"][0]["control"].update(min=10, max=1),
        lambda d: d["bindings"][1]["control"].update(locked=False),
        lambda d: d["bindings"][1]["control"].update(locked="true"),
        lambda d: d["repairs"].append(dict(surface_or_line_id="missing", segments=[])),
        lambda d: d["annotations"][0].update(text_id="missing"),
        lambda d: d["frame"].update(
            px_per_m=dict(number=-1, unit="px/m", status="given", source="user", confidence=1)
        ),
    ],
)
def test_strict_finite_document_and_references(mutate):
    document = raw()
    mutate(document)
    with pytest.raises((ValidationError, ValueError)):
        Scene.model_validate(document)


def test_unknown_objects_are_retained_and_warning_is_idempotent():
    document = raw()
    document["bodies"][0]["type"] = "unknown_body"
    scene = Scene.model_validate(document)
    assert scene.bodies[0].type == "unknown_body"
    assert [(w.code, w.ref) for w in scene.warnings] == [("unknown_type", "B1")]
    assert Scene.model_validate_json(scene.model_dump_json(by_alias=True)) == scene


def test_missing_defaults_are_explicit_and_null_is_never_overwritten():
    document = raw("spring_horizontal")
    del document["constants"]
    del document["bodies"][0]["mass"]
    del document["links"][0]["damping"]
    del document["links"][0]["rest_length_m"]
    del document["frame"]["px_per_m"]
    before = copy.deepcopy(document)
    scene = Scene.model_validate(document)
    assert document == before
    for value, expected in [
        (scene.constants.g, 9.81),
        (scene.bodies[0].mass, 1),
        (scene.links[0].damping, 0),
        (scene.links[0].rest_length_m, 0.5),
        (scene.frame.px_per_m, 100),
    ]:
        assert value.number == expected
        assert (value.status, value.source, value.confidence) == ("assumed", "prior", 0)
    document["bodies"][0]["mass"] = dict(
        number=None, unit="kg", status="given", source="ocr", confidence=0.2
    )
    assert Scene.model_validate(document).bodies[0].mass.number is None


def test_generated_schema_matches_model_and_installed_namespaces():
    schema = json.loads((ROOT / "docs/mechanics/schema.json").read_text(encoding="utf-8"))
    assert schema == Scene.model_json_schema(mode="serialization", by_alias=True)
    for prefix in ("augphys", "circuit_sim"):
        # The compatibility namespaces intentionally share the root module.
        # Exercise each supported import in its own interpreter, as M1 does;
        # importing both trees into this pytest process pollutes legacy patches.
        subprocess.run(
            [
                sys.executable,
                "-c",
                "import importlib, pathlib; "
                f"m=importlib.import_module('{prefix}.backend.tools.mechanics.paint_scene'); "
                f"assert pathlib.Path(m.__file__).resolve().is_relative_to({str(ROOT)!r})",
            ],
            cwd=ROOT.parent,
            check=True,
            capture_output=True,
            text=True,
        )


def test_spring_primitive_preserves_leads_and_finite_short_compression():
    points = spring_points((0, 0), (100, 0), 8)
    assert points[:2] == [(0, 0), (12, 0)]
    assert points[-2:] == [(88, 0), (100, 0)]
    assert spring_points((0, 0), (8, 0)) == [(0, 0), (8, 0)]
