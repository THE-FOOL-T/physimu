"""User raster regression: controlled compiler evidence and real local OCR separate."""

import math
import os
from pathlib import Path

import cv2
import numpy as np
import pytest

from circuit_sim.backend.domains.mechanics.classical import pendulum_proposals
from circuit_sim.backend.domains.mechanics.detect import checkpoint_readiness
from circuit_sim.backend.domains.mechanics.engine import analyze_mechanics_page
from circuit_sim.backend.domains.mechanics.geometry import fit_line
from circuit_sim.backend.domains.mechanics.labels import read_tokens
from circuit_sim.backend.domains.mechanics.ocr import fuse_mechanics
from circuit_sim.backend.domains.mechanics.scene import Scene

SOURCE = Path(__file__).parent / "assets/user-pendulum.png"


def raster():
    image = cv2.imread(str(SOURCE))
    assert image is not None, "The exact user raster is mandatory for this regression."
    return image


def assert_pendulum(result, mass=0.5, length=1.2, angle=15.0):
    scene = Scene.model_validate(result["scene"])
    assert scene.archetype == "pendulum", result["reason"]
    assert len(scene.bodies) == len(scene.links) == 1
    body, link = scene.bodies[0], scene.links[0]
    assert body.mass.number == mass and body.mass.source == "ocr"
    assert link.length_m.number == length and link.length_m.source == "ocr"
    assert scene.params["release_angle"].number == angle
    assert scene.params["release_angle"].source == "ocr"
    assert {link.a.ref, link.b.ref} == {"pivot", body.id}
    assert math.dist(link.b.point, body.anchor) < 1
    assert body.initial.position.x.number == pytest.approx(length * math.sin(math.radians(angle)))
    assert body.initial.position.y.number == pytest.approx(length * math.cos(math.radians(angle)))
    paths = {b.path: b for b in scene.bindings}
    for path in (f"bodies.{body.id}.mass", f"links.{link.id}.length_m", "params.release_angle"):
        assert path in paths and paths[path].labels
        assert any(a.bound_to == path and a.id in paths[path].labels for a in scene.annotations)
    assert result["readiness"]["physics_supported"]
    return scene


@pytest.mark.parametrize("mass,length,angle", [(0.5, 1.2, 15.0), (0.75, 2.4, 22.0)])
def test_controlled_perception_compiles_raster_with_variable_readings(mass, length, angle):
    image = raster()
    boxes, _ = pendulum_proposals(image)
    # Controlled model-like boxes, with the actual support line's measured center.
    support = fit_line(image, boxes[0].bbox, orientation="ceiling")["points"]
    y = sum(p[1] for p in support) / 2
    cx = (boxes[1].bbox[0] + boxes[1].bbox[2]) / 2
    boxes[1].bbox = [cx - 3, y - 3, cx + 3, y + 3]
    texts = [
        dict(text=f"L = {length} m", bbox=[628, 245, 803, 292], confidence=0.96),
        dict(text=f"m = {mass} kg", bbox=[403, 598, 599, 657], confidence=0.98),
        dict(text=f"{angle} deg", bbox=[515, 228, 591, 284], confidence=0.99),
    ]
    result = analyze_mechanics_page(
        image, detector=lambda *a, **k: boxes, text_reader=lambda *a, **k: (texts, [])
    )
    assert_pendulum(result, mass, length, angle)
    assert result["diagnostics"]["recognition"]["method"] == "controlled_perception"


def test_real_user_raster_missing_detector_runs_classical_geometry_and_actual_hybrid_ocr(
    monkeypatch, tmp_path
):
    """Mandatory Test B: no injected detector, OCR, values or preauthored scene."""
    monkeypatch.setenv("MECHANICS_MODEL", str(tmp_path / "deliberately-absent.pt"))
    events = []
    result = analyze_mechanics_page(
        raster(),
        {"use_label_reader": False},
        progress=lambda stage, partial=None: events.append((stage, partial)),
    )
    scene = assert_pendulum(result)
    assert result["diagnostics"]["recognition"]["method"] == "classical_vision"
    assert result["diagnostics"]["recognition"]["model_status"] == "unavailable"
    assert len(result["diagnostics"]["classical"]["selected"]["alternatives"]) == 2
    assert len([a for a in scene.annotations if a.id.startswith("alternate_state_")]) == 2
    assert (
        len(
            [
                r
                for r in result["diagnostics"]["evidence"]["relationships"]
                if r["type"] == "ALTERNATE_STATE_OF"
            ]
        )
        == 2
    )
    assert all(
        result["timings"][stage] is not None
        for stage in ("text", "geometry", "associate", "validate")
    )
    assert {r["kind"] for r in result["diagnostics"]["assignments"] if r["accepted"]} >= {
        "mass",
        "length",
        "angle",
    }
    assert any(stage == "associate" and p and p.get("relationships") for stage, p in events)
    assert not any(b.id.startswith("manual_") for b in scene.bodies)
    assert result["diagnostics"]["label_reader"]["crops_sent"] == 0


@pytest.mark.parametrize("scale,padding", [(0.7, 23), (1.25, 41)])
def test_classical_geometry_is_not_tied_to_filename_or_pixel_coordinates(scale, padding):
    image = raster()
    original, _ = pendulum_proposals(image)
    resized = cv2.resize(image, None, fx=scale, fy=scale)
    moved = cv2.copyMakeBorder(
        resized, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=(255, 255, 255)
    )
    transformed, report = pendulum_proposals(moved)
    assert report["accepted"] and len(transformed) == 4

    def center(d):
        return np.array([(d.bbox[0] + d.bbox[2]) / 2, (d.bbox[1] + d.bbox[3]) / 2])

    assert np.linalg.norm(center(transformed[2]) - (center(original[2]) * scale + padding)) < 4


def test_classical_rejects_blank_and_equally_plausible_physical_bobs():
    image = np.full((400, 600, 3), 255, np.uint8)
    assert not pendulum_proposals(image)[0]
    cv2.line(image, (100, 50), (500, 50), (0, 0, 0), 3)
    for x in (220, 380):
        cv2.line(image, (300, 50), (x, 250), (0, 0, 0), 2)
        cv2.circle(image, (x, 250), 19, (0, 0, 0), -1)
    boxes, report = pendulum_proposals(image)
    assert not boxes and report["reason"] == "ambiguous_pendulum_candidates"
    assert len(report["candidates"]) >= 2
    chosen, confirmed = pendulum_proposals(image, candidate=1)
    assert len(chosen) == 4 and confirmed["confirmed_by_user"]
    assert not pendulum_proposals(image, candidate=100)[0]


def test_orientation_alternatives_are_retained_without_becoming_confident_physical_conflicts():
    row = dict(
        text="L = 2.4 m",
        bbox=[10, 10, 160, 40],
        confidence=0.96,
        rotation=0,
        classifier_result=[["0", 0.99]],
        alternatives=[dict(text="7 m", bbox=[10, 10, 160, 40], confidence=0.9, rotation=180)],
    )
    fused = fuse_mechanics([row], {})
    assert fused[0]["alternatives"][0]["binding_eligible"] is False
    assert read_tokens(fused)[0].number == 2.4 and not read_tokens(fused)[0].conflict
    row["alternatives"][0]["rotation"] = 0
    assert read_tokens(fuse_mechanics([row], {}))[0].conflict


def test_real_checkpoint_configuration_when_explicitly_supplied(monkeypatch):
    path = os.environ.get("MECHANICS_TEST_MODEL")
    if not path or not Path(path).is_file():
        pytest.skip("Supply MECHANICS_TEST_MODEL for actual local 21-class checkpoint inference.")
    monkeypatch.setenv("MECHANICS_MODEL", path)
    readiness = checkpoint_readiness(load=True)
    assert readiness["status"] == "ready" and readiness["actual_class_count"] == 21
    result = analyze_mechanics_page(raster(), {"use_label_reader": False})
    assert result["diagnostics"]["recognition"]["model_status"] == "ready"
    assert result["diagnostics"].get("model_detections") or result["diagnostics"]["detections"]
    assert_pendulum(result)
