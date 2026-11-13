"""Mechanics synthetic pen/warp/mask/geometry/e2e checks, never real accuracy."""

import json
import random
import shutil
import uuid

import cv2
import numpy as np
import pytest
from PIL import Image

from circuit_sim.backend.domains.mechanics.engine import analyze_mechanics_page
from circuit_sim.backend.domains.mechanics.scene import Scene
from circuit_sim.backend.domains.mechanics.sprites import body_mask
from circuit_sim.backend.tools.mechanics.build_fixtures import fixtures
from circuit_sim.backend.tools.mechanics.common import ROOT, load_dataset, read_labels
from circuit_sim.backend.tools.mechanics.handwriting import deform, elastic_parameters, inverse_maps
from circuit_sim.backend.tools.mechanics.make_synthetic import generate, sample, project_point
from circuit_sim.backend.tests.mechanics.handwriting_probe import case, measurements


def test_smooth_elastic_inverse_maps_recover_destination_pixels():
    settings = elastic_parameters(random.Random(42))
    x, y = inverse_maps(240, 180, settings)
    destination = deform(np.stack([x, y], axis=-1), settings)
    yy, xx = np.mgrid[:180, :240]
    assert np.max(np.abs(destination - np.stack([xx, yy], axis=-1))) < 2e-5


def test_strong_profile_reproduces_pixels_and_keeps_mask_boxes_and_scene_in_native_coordinates():
    source = fixtures()["incline"]
    args = (source, ("incline_block", "handwritten", True, False, True))
    a = sample(*args, random.Random(23), "TEST.png", handwriting="strong")
    b = sample(*args, random.Random(23), "TEST.png", handwriting="strong")
    image, mask, objects, scene, settings = a
    assert np.array_equal(np.array(image), np.array(b[0])) and np.array_equal(mask, b[1])
    assert settings == b[4] and settings["elastic"] and settings["notebook_ruling"]
    point = project_point(source.surfaces[0].polyline[0], np.array(settings["homography"]))
    assert scene.surfaces[0].polyline[0] == pytest.approx(deform(point, settings["elastic"]))
    assert len(scene.surfaces[0].polyline) > 2
    for obj in objects:
        y, x = np.where(mask == obj["mask_index"])
        if len(x):
            assert x.min() >= obj["bbox"][0] and x.max() < obj["bbox"][2]
            assert y.min() >= obj["bbox"][1] and y.max() < obj["bbox"][3]
        body = next((body for body in scene.bodies if body.id == obj["id"]), None)
        if body:
            assert list(body.bbox) == obj["bbox"]


def test_strong_generator_writes_trainable_synthetic_only_manifest_and_aligned_labels():
    base = ROOT / ".cache/m6-generator-tests"
    out = base / uuid.uuid4().hex
    try:
        generate(out, 8, 74, small=True, handwriting="strong")
        manifest = load_dataset(out)
        assert manifest["origin"] == "synthetic" and len(manifest["records"]) == 8
        for row in manifest["records"]:
            with Image.open(out / row["image"]) as raster:
                labels = read_labels(out / row["label"], *raster.size)
            objects = json.loads(
                (out / "objects" / (out / row["image"]).with_suffix(".json").name).read_text(
                    encoding="utf-8"
                )
            )
            assert len(labels) == len(objects)
            for (_, box), obj in zip(labels, objects):
                assert box == pytest.approx(obj["bbox"], abs=2e-6)
            if row["style"] == "handwritten":
                assert row["augmentation"]["elastic"]
    finally:
        if out.exists():
            assert out.resolve().is_relative_to(base.resolve())
            shutil.rmtree(out)


def test_small_gaps_close_for_handwritten_body_but_large_open_outlines_remain_unmeasured():
    image = np.full((240, 300, 3), 255, np.uint8)
    cv2.rectangle(image, (100, 100), (180, 160), (20, 20, 20), 2)
    image[97:104, 135:140] = 255
    assert body_mask(image, [98, 98, 182, 162])["warning"] == "mask_unmeasured"
    fit = body_mask(image, [98, 98, 182, 162], style="handwritten")
    assert fit["warning"] is None
    assert cv2.contourArea(np.array(fit["polygon"], np.float32)) > 4500
    image[97:104, 128:150] = 255
    assert body_mask(image, [98, 98, 182, 162], style="handwritten")["warning"] == "mask_unmeasured"


def test_wobbled_line_circle_and_spring_have_measured_errors():
    result = measurements()
    assert max(r["angle_error_deg"] for r in result["lines"]) < 1.5
    assert max(r["length_error_px"] for r in result["lines"]) < 5
    assert result["circle"]["center_error_px"] < 1
    assert result["circle"]["radius_error_px"] < 1
    assert abs(result["spring"]["measured_coils"] - 10) <= 1
    assert max(result["spring"]["endpoint_errors_px"]) < 9


@pytest.mark.parametrize("name", list(fixtures()))
def test_handwritten_detector_stub_flows_to_valid_editable_scene(name):
    image, truth, detector, reader = case(name)
    result = analyze_mechanics_page(
        image, dict(style="handwritten"), detector=detector, text_reader=reader
    )
    checked = Scene.model_validate(result["scene"])
    assert checked.archetype == truth.archetype
    assert checked.meta.style == "handwritten"
    assert result["provenance"] in {"partial", "unsupported"}
    assert any(w["code"] == "handwriting_edit_expected" for w in result["warnings"])
    assert result["diagnostics"]["label_reader"]["crops_sent"] == 0
    assert "netlist" not in result and "solution" not in result
