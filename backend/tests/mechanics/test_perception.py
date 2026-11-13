"""Measured synthetic evidence; oracle boxes/raw OCR are not recognition results."""

import copy
import importlib
import json
import math
import threading

import cv2
import numpy as np
import pytest

from circuit_sim.backend.app.jobs import Cancelled, JobStore
from circuit_sim.backend.core import models
from circuit_sim.backend.domains.mechanics import geometry
from circuit_sim.backend.domains.mechanics.associate import associate
from circuit_sim.backend.domains.mechanics.corrections import save_correction
from circuit_sim.backend.domains.mechanics.engine import (
    analyze_mechanics_page,
    STAGES,
    route_domain,
)
from circuit_sim.backend.domains.mechanics.labels import parse, read_tokens
from circuit_sim.backend.domains.mechanics.perception import measure, calibrate
from circuit_sim.backend.domains.mechanics.scene import Scene
from circuit_sim.backend.domains.mechanics.sprites import body_mask, repairs
from circuit_sim.backend.domains.mechanics.validate import finalize, interpretations
from circuit_sim.backend.tools.mechanics.build_fixtures import fixtures
from circuit_sim.backend.tools.mechanics.paint_scene import spring_points

from circuit_sim.backend.tests.mechanics.perception_fixtures import case


def paper():
    return np.full((400, 600, 3), 255, np.uint8)


@pytest.mark.parametrize("angle", [0, 15, 30, 60, 90, -30])
def test_line_measurement_against_drawn_pixels(angle):
    im = paper()
    a = np.array([150.0, 250.0])
    b = a + [200 * math.cos(math.radians(angle)), -200 * math.sin(math.radians(angle))]
    cv2.line(im, tuple(a.astype(int)), tuple(np.rint(b).astype(int)), (30, 30, 30), 2)
    fit = geometry.fit_line(im, [0, 0, 600, 400])
    assert abs((fit["angle_deg"] - angle + 90) % 180 - 90) < 0.7  # undirected line
    assert abs(fit["length_px"] - 200) < 4
    assert fit["residual_px"] < 2


def test_circle_and_pendulum_measured_not_box_angle():
    im = paper()
    cv2.circle(im, (350, 250), 24, (30, 30, 30), 2)
    circle = geometry.fit_circle(im, [325, 224, 377, 275])
    assert math.dist(circle["center"], [350, 250]) < 0.8
    assert abs(circle["radius_px"] - 24) < 1
    actual = geometry.pendulum([250, 50], circle["center"])
    assert abs(actual["length_px"] - math.hypot(100, 200)) < 0.8
    assert abs(actual["angle_deg"] - math.degrees(math.atan(0.5))) < 0.3


def test_skeleton_masks_body_and_measures_spring_coils():
    im = paper()
    pts = spring_points([80, 180], [400, 180], 10)
    cv2.polylines(im, [np.rint(pts).astype(np.int32)], False, (30, 30, 30), 2)
    cv2.rectangle(im, (400, 160), (450, 200), (30, 30, 30), 2)
    fit = geometry.spring(im, [70, 155, 405, 205], [[400, 155, 455, 205]])
    assert abs(fit["coils"] - 10) <= 1
    assert math.dist(fit["endpoints"][0], [80, 180]) < 15
    assert fit["endpoints"][1][0] <= 400
    assert all(p[0] < 400 for p in fit["points"])


def test_parabola_native_tangent_style_mask_and_repairs():
    im = paper()
    xs = np.linspace(50, 450, 250)
    points = [[x, 0.002 * (x - 200) ** 2 + 70] for x in xs]
    cv2.polylines(im, [np.rint(points).astype(np.int32)], False, (32, 40, 48), 2)
    fit = geometry.trajectory_arc(im, [40, 60, 460, 210], [50, 115])
    assert abs(fit["angle_deg"] - math.degrees(math.atan(0.6))) < 1
    assert abs(fit["coefficients"][0] - 0.002) < 0.0001
    style = geometry.measure_style(im)
    assert style["paper_color"] == "#ffffff" and style["ink_color"] == "#302820"
    assert 1 <= style["stroke_px"] <= 4
    im = paper()
    cv2.rectangle(im, (200, 200), (260, 240), (30, 30, 30), 2)
    mask = body_mask(im, [200, 200, 260, 240], [])
    assert len(mask["polygon"]) >= 4 and mask["confidence"] > 0
    fixes = repairs(
        [dict(bbox=[200, 200, 260, 240])],
        [dict(id="floor", polyline=[[100.0, 220.0], [400.0, 220.0]])],
    )
    assert len(fixes) == 1 and fixes[0]["segments"][0][0][0] >= 200


@pytest.mark.parametrize(
    "method",
    [
        geometry.fit_line,
        geometry.fit_circle,
        geometry.trace,
        geometry.spring,
        geometry.trajectory_arc,
    ],
)
def test_empty_geometry_is_explicit(method):
    with pytest.raises(ValueError, match="unmeasured"):
        method(paper(), [10, 10, 200, 200])


@pytest.mark.parametrize(
    "text,kind,number,unit",
    [
        ("5 kg", "mass", 5, "kg"),
        ("m₁ = 2 kg", "mass", 2, "kg"),
        ("300 g", "mass", 0.3, "kg"),
        ("θ = 37°", "angle", 37, "deg"),
        ("30 deg", "angle", 30, "deg"),
        ("μs = 0.3", "friction_static", 0.3, "1"),
        ("μₖ = 0.2", "friction_kinetic", 0.2, "1"),
        ("v0 = 15 m/s", "speed", 15, "m/s"),
        ("L = 40 cm", "length", 0.4, "m"),
        ("1.5 m", "length", 1.5, "m"),
        ("k = 200 N/m", "spring_constant", 200, "N/m"),
        ("F = 25 N", "force", 25, "N"),
        ("g = 9.8 m/s²", "gravity", 9.8, "m/s^2"),
        ("c = 0.5 kg/s", "damping", 0.5, "kg/s"),
        ("৩ কেজি", "mass", 3, "kg"),
        ("৪০ সেন্টিমিটার", "length", 0.4, "m"),
        ("θ = ৩০ ডিগ্রি", "angle", 30, "deg"),
        ("2e2 N/m", "spring_constant", 200, "N/m"),
    ],
)
def test_mechanics_grammar(text, kind, number, unit):
    (token,) = parse(text)
    assert (token.kind, token.unit) == (kind, unit)
    assert token.number == pytest.approx(number)


@pytest.mark.parametrize("name", ["m", "M", "g", "m₁"])
def test_bare_names_have_no_unit(name):
    (token,) = parse(name)
    assert token.kind == "name" and token.number is None


def test_unknown_number_stays_unplaced_and_alternative_uses_mechanics_grammar():
    assert parse("25")[0].kind == "unplaced"
    assert parse("25 metres")[0].kind == "unplaced"
    (token,) = read_tokens(
        [
            dict(
                text="200 Ω",
                bbox=[0, 0, 20, 20],
                confidence=0.99,
                alternatives=[dict(text="200 N/m", confidence=0.6)],
            )
        ]
    )
    assert token.kind == "spring_constant" and token.confidence == 0.6


def test_assignment_hungarian_names_distance_user_values_and_unplaced():
    scene = fixtures()["collision"].model_dump(mode="json", by_alias=True)
    a, b = scene["bodies"]
    a["mass"]["source"] = "user"
    a["mass"]["status"] = "user"
    b["mass"].update(source="prior", status="assumed")
    old = copy.deepcopy(a["mass"])
    rows = associate(
        scene,
        [
            *parse("4 kg", a["bbox"]),
            *parse("300 g", b["bbox"]),
            *parse("m", b["bbox"]),
            *parse("10 N", [0, 0, 5, 5]),
            *parse("5 kg", [1500, 1500, 1510, 1510]),
        ],
    )
    assert a["mass"] == old and not rows[0]["accepted"]
    assert b["mass"]["number"] == 0.3 and b["mass"]["status"] == "given"
    assert rows[2]["ref"] == b["id"]
    assert all(not r["accepted"] and r["unplaced_path"] for r in rows[3:])
    assert len([k for k in scene["params"] if k.startswith("unplaced_")]) == 3


@pytest.mark.parametrize("name", list(fixtures()))
def test_oracle_box_ocr_pipeline_for_all_painted_fixtures(name):
    image, truth, detector, reader = case(name)
    progress = []
    result = analyze_mechanics_page(
        image,
        {"style": "printed"},
        lambda s, p=None: progress.append((s, p)),
        detector=detector,
        text_reader=reader,
    )
    scene = Scene.model_validate(result["scene"])
    assert scene.archetype == truth.archetype
    assert len(scene.bodies) == len(truth.bodies)
    assert result["provenance"] == "partial"  # priors are disclosed, never oracle-completed
    assert "netlist" not in result and "solution" not in result
    assert list(dict.fromkeys(s for s, _ in progress)) == list(STAGES)
    assert any(p and p.get("detections") for _, p in progress)
    assert any(p and p.get("texts") for _, p in progress)
    assert all(t is not None and t >= 0 for t in result["timings"].values())
    assert result["diagnostics"]["alternatives"]
    for got in scene.bodies:
        expected = min(truth.bodies, key=lambda b: math.dist(b.anchor, got.anchor))
        assert got.mass.number == expected.mass.number
    objects = {
        o.id
        for group in (scene.bodies, scene.surfaces, scene.annotations, scene.pulleys)
        for o in group
    }
    assert all(
        link.a.ref in objects and link.b.ref in objects and link.a.ref != link.b.ref
        for link in scene.links
    )


def test_empty_and_unknown_boxes_retain_image_and_reason():
    detect = importlib.import_module("circuit_sim.backend.domains.mechanics.detect")
    result = analyze_mechanics_page(
        paper(),
        detector=lambda *a, **k: [detect.Detection("unknown", "unseen", [20.0, 20.0, 50.0, 50.0])],
        text_reader=lambda *a, **k: ([], []),
    )
    assert result["provenance"] == "unsupported" and result["reason"]
    assert result["scene"]["annotations"][0]["type"] == "unseen"
    assert route_domain(paper())["reason"] == "domain_unknown"


def test_multiple_surface_interpretations_and_invalid_physics():
    scene = fixtures()["incline"].model_dump(mode="json", by_alias=True)
    best, alternatives = interpretations(scene, {})
    assert len(alternatives) > 1
    assert best[0]["bodies"][0]["on_surface"] == scene["surfaces"][0]["id"]
    scene["bodies"][0]["mass"]["number"] = -1.0
    assert finalize(scene) and scene["meta"]["provenance"] == "unsupported"
    assert any(w["code"] == "invalid_mass" for w in scene["warnings"])


def test_domain_lease_eviction_serialization_and_wait_cancellation(monkeypatch):
    events = []
    monkeypatch.setattr(
        models,
        "_releases",
        {
            "circuit": lambda: events.append("drop circuit"),
            "mechanics": lambda: events.append("drop mechanics"),
        },
    )
    entered = threading.Event()
    ended = threading.Event()

    def queued():
        def check():
            entered.set()
            raise Cancelled()

        with pytest.raises(Cancelled), models.model_lease("circuit", check):
            pytest.fail("Cancelled waiter acquired model")
        ended.set()

    with models.model_lease("mechanics"):
        assert events == ["drop circuit"]
        with models.model_lease("mechanics"):
            assert events == ["drop circuit"]
        thread = threading.Thread(target=queued)
        thread.start()
        assert entered.wait(2) and ended.wait(2)
    thread.join()
    with models.model_lease("circuit"):
        assert events == ["drop circuit", "drop mechanics"]


def test_cooperative_pipeline_cancel_never_returns_result():
    im, _, detector, reader = case("pendulum")
    store = JobStore(limit=1)
    entered, release = threading.Event(), threading.Event()

    def slow(image, check):
        entered.set()
        assert release.wait(3)
        check()
        return detector(image, check)

    try:
        job = store.start(
            lambda p: analyze_mechanics_page(im, progress=p, detector=slow, text_reader=reader),
            stages=STAGES,
        )
        assert entered.wait(3)
        store.cancel(job)
        release.set()
        store.jobs[job]["future"].result(timeout=3)
        assert store.get(job)["result"] is None and store.get(job)["error"]["code"] == "cancelled"
    finally:
        release.set()
        store.executor.shutdown(wait=True)


def test_corrections_native_dimensions_and_unreviewed_storage(tmp_path):
    im, scene, _, _ = case("pendulum")
    data = cv2.imencode(".png", im)[1].tobytes()
    result = save_correction(data, scene.model_dump_json(by_alias=True), root=tmp_path)
    folder = tmp_path / "data/corrections/mechanics" / result["id"]
    assert result["human_reviewed"] is False
    assert json.loads((folder / "consent.json").read_text())["human_reviewed"] is False
    invalid = scene.model_copy(deep=True)
    invalid.image.width += 1
    with pytest.raises(ValueError, match="dimensions"):
        save_correction(data, invalid.model_dump_json(by_alias=True), root=tmp_path)


def test_dimension_label_calibrates_native_scale_from_measured_line():
    from circuit_sim.backend.domains.mechanics.detect import Detection

    im = paper()
    cv2.line(im, (50, 80), (250, 80), (30, 30, 30), 2)
    cv2.rectangle(im, (300, 200), (350, 240), (30, 30, 30), 2)
    scene, evidence, _, confidences = measure(
        im,
        [
            Detection("a", "dimension_line", [45.0, 75.0, 255.0, 85.0]),
            Detection("b", "block", [300.0, 200.0, 350.0, 240.0]),
        ],
        "en",
        "printed",
        lambda: None,
    )
    rows = associate(scene, parse("2 m", [130, 45, 170, 65]), confidences)
    scene = calibrate(scene, rows, evidence)
    assert scene["frame"]["px_per_m"]["status"] == "given"
    assert abs(scene["frame"]["px_per_m"]["number"] - 100) < 2


def test_two_collision_panels_keep_after_labels_as_checks_only():
    from circuit_sim.backend.domains.mechanics.detect import Detection

    im, _, detector, _ = case("collision")
    canvas = np.full((520, 1800, 3), 255, np.uint8)
    canvas[:, :800] = im
    canvas[:, 1000:] = im
    first = detector(im)
    second = [
        Detection(
            d.id + "after",
            d.type,
            [d.bbox[0] + 1000, d.bbox[1], d.bbox[2] + 1000, d.bbox[3]],
            d.confidence,
        )
        for d in first
    ]
    texts = []
    # TEST OCR supplies spatial body-speed readings, never a completed graph.
    for dx in (0, 1000):
        texts.extend(
            [
                dict(text="1 kg", bbox=[182.0 + dx, 332.0, 222.0 + dx, 352.0], confidence=1.0),
                dict(text="1 kg", bbox=[382.0 + dx, 332.0, 422.0 + dx, 352.0], confidence=1.0),
                dict(text="2 m/s", bbox=[180.0 + dx, 285.0, 220.0 + dx, 305.0], confidence=1.0),
                dict(text="-1 m/s", bbox=[380.0 + dx, 285.0, 420.0 + dx, 305.0], confidence=1.0),
            ]
        )
    result = analyze_mechanics_page(
        canvas,
        dict(style="printed"),
        detector=lambda *a, **k: first + second,
        text_reader=lambda *a, **k: (texts, []),
    )
    assert result["scene"]["archetype"] == "collision_1d"
    check = result["diagnostics"]["collision_panels"]
    assert len(check["observed"]) == 2 and check["comparison"] == "frontend_solver_only"
    assert result["scene"]["constraints"][0]["type"] == "after_velocity"
    assert all(b["anchor"][0] < 1000 for b in result["scene"]["bodies"])


def test_correction_api_rejects_no_consent_and_invalid_scene_without_writes(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient
    from circuit_sim.backend.app import main
    from circuit_sim.backend.domains.mechanics import corrections

    im, scene, _, _ = case("pendulum")
    file = {"image": ("diagram.png", cv2.imencode(".png", im)[1].tobytes(), "image/png")}
    original = corrections.save_correction
    monkeypatch.setattr(
        corrections,
        "save_correction",
        lambda data, scene_json, root: original(data, scene_json, tmp_path),
    )
    client = TestClient(main.app)
    assert (
        client.post(
            "/api/corrections",
            files=file,
            data=dict(domain="mechanics", scene=scene.model_dump_json(by_alias=True)),
        ).status_code
        == 400
    )
    assert not (tmp_path / "data").exists()
    bad = client.post(
        "/api/corrections", files=file, data=dict(domain="mechanics", scene="{}", opt_in="true")
    )
    assert bad.status_code == 422 and bad.json()["detail"]["code"] == "invalid_correction"
    assert not (tmp_path / "data").exists()
    good = client.post(
        "/api/corrections",
        files=file,
        data=dict(domain="mechanics", scene=scene.model_dump_json(by_alias=True), opt_in="true"),
    )
    assert good.status_code == 200 and not good.json()["human_reviewed"]
