"""Pixel/annotation alignment and seeded R1 mix tests, never real accuracy."""

import json
from pathlib import Path
import random
import shutil
import uuid

import numpy as np
from PIL import Image
import pytest

from circuit_sim.backend.domains.mechanics.scene import Scene
from circuit_sim.backend.tools.mechanics.build_fixtures import fixtures
from circuit_sim.backend.tools.mechanics.common import ROOT, NAMES, load_dataset, read_labels
from circuit_sim.backend.tools.mechanics.leakage import audit
from circuit_sim.backend.tools.mechanics.make_synthetic import generate, schedules, sample
from circuit_sim.backend.tools.mechanics.synthetic_painter import render


@pytest.fixture(scope="module")
def corpus():
    base = (ROOT / ".cache/m4-synthetic-tests").resolve()
    root = base / uuid.uuid4().hex
    root.mkdir(parents=True)
    first = root / "a"
    second = root / "b"
    generate(first, 16, 17, small=True)
    generate(second, 16, 17, small=True)
    yield first, second
    assert root.resolve().is_relative_to(base) and base.is_relative_to(ROOT)
    shutil.rmtree(root)


def test_default_mix_has_exact_archetype_style_mirror_and_label_coverage():
    rows = schedules(600, 42)
    from collections import Counter

    assert set(Counter(r[0] for r in rows).values()) == {75}
    assert Counter(r[1] for r in rows) == {
        "printed": 180,
        "scan": 120,
        "handwritten": 180,
        "photo": 120,
    }
    assert (
        sum(r[2] for r in rows) == 300
        and sum(r[3] for r in rows) == 150
        and sum(r[4] for r in rows) == 60
    )
    assert schedules(600, 42) == rows and schedules(600, 43) != rows


def test_seed_reproduces_every_image_label_scene_mask_and_relative_manifest(corpus):
    a, b = corpus
    files = [p.relative_to(a) for p in a.rglob("*") if p.is_file() and p.name != "data.yaml"]
    assert files and all((a / p).read_bytes() == (b / p).read_bytes() for p in files)
    manifest = load_dataset(a)
    assert len(manifest["records"]) == 16
    assert audit(manifest, a, a / "missing-frozen")["passed"]


def test_all_labels_match_actual_amodal_extents_and_visible_mask_pixels(corpus):
    root, _ = corpus
    manifest = load_dataset(root)
    classes = set()
    for row in manifest["records"]:
        stem = Path(row["image"]).stem
        scene = Scene.model_validate_json(
            (root / f"scenes/{stem}.json").read_text(encoding="utf-8")
        )
        with Image.open(root / row["image"]) as image:
            w, h = image.size
        assert 600 <= w <= 1400 and 600 <= h <= 1400
        objects = json.loads((root / f"objects/{stem}.json").read_text())
        labels = read_labels(root / row["label"], w, h)
        mask = np.array(Image.open(root / f"masks/{stem}.png"))
        assert mask.shape == (h, w)
        assert len(objects) == len(labels)
        for obj, (cls, box) in zip(objects, labels):
            classes.add(obj["class"])
            assert NAMES[cls] == obj["class"]
            assert box == pytest.approx(obj["bbox"], abs=2e-6)
            y, x = np.where(mask == obj["mask_index"])
            if len(x):
                assert x.min() >= obj["bbox"][0] and x.max() < obj["bbox"][2]
                assert y.min() >= obj["bbox"][1] and y.max() < obj["bbox"][3]
            body = next((body for body in scene.bodies if body.id == obj["id"]), None)
            if body:
                assert list(body.bbox) == obj["bbox"]
            annotation = next(
                (a for a in scene.annotations if a.id == obj["id"] and a.type == "label"), None
            )
            if annotation:
                assert list(annotation.geometry.bbox) == obj["bbox"]
        assert 0.5 <= row["augmentation"]["scale"] <= 1.6
    assert classes == set(NAMES)
    counts = json.loads((root / "counts.json").read_text())
    assert min(counts["classes"].values()) >= 2


def test_reflection_keeps_text_readable_instead_of_backwards():
    scene = fixtures()["pendulum"]
    args = {
        "style": "printed",
        "font_size": 18,
        "font_variant": 1,
        "arrow_style": "filled",
        "hatch_spacing": 15,
    }
    _, normal = render(scene, random.Random(1), **args)
    _, mirrored = render(scene, random.Random(1), **args, mirror_text=True)
    a = next(o for o in normal if o["class"] == "text_label")
    b = next(o for o in mirrored if o["id"] == a["id"])
    box = a["mask"].getbbox()
    assert (
        np.array(b["mask"].crop(box)).tolist() == np.fliplr(np.array(a["mask"].crop(box))).tolist()
    )
    assert not np.array_equal(np.array(a["mask"]), np.array(b["mask"]))


def test_rotation_and_perspective_preserve_transformed_native_geometry():
    source = fixtures()["incline"]
    for style in ("scan", "photo", "handwritten"):
        image, mask, objects, scene, settings = sample(
            source, ("incline_block", style, True, False, True), random.Random(23), "sample.png"
        )
        H = np.array(settings["homography"])
        point = H @ np.array([*source.surfaces[0].polyline[0], 1.0])
        assert scene.surfaces[0].polyline[0] == pytest.approx(point[:2] / point[2])
        assert mask.shape == (image.height, image.width) and objects
        assert scene.meta.language == "bn"


def test_production_count_requires_400_to_800_and_never_overwrites(corpus):
    root, _ = corpus
    with pytest.raises(ValueError, match="400"):
        generate(root / "invalid", 32)
    with pytest.raises(ValueError, match="new or empty"):
        generate(root, 16, small=True)
