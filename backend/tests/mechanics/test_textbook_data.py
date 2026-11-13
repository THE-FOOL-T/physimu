"""Next synthetic corpus: pixel ownership, real extents and opt-in reproducibility."""

import json
from pathlib import Path
import random
import shutil
import uuid

import numpy as np
from PIL import Image
import pytest

from circuit_sim.backend.tools.mechanics.audit_sizes import audit
from circuit_sim.backend.tools.mechanics.build_fixtures import fixtures
from circuit_sim.backend.tools.mechanics.common import ROOT, NAMES, load_dataset, read_labels
from circuit_sim.backend.tools.mechanics.make_synthetic import generate, sample, variant
from circuit_sim.backend.tools.mechanics.synthetic_painter import render
from circuit_sim.backend.tools.mechanics.textbook import prepare, spring_path, separate


@pytest.fixture(scope="module")
def corpus():
    base = ROOT / ".cache/textbook-tests"
    root = base / uuid.uuid4().hex
    try:
        for name in ("a", "b"):
            generate(root / name, 16, 73, small=True, appearance="textbook", handwriting="strong")
        yield root / "a", root / "b"
    finally:
        if root.exists():
            assert root.resolve().is_relative_to(base.resolve())
            shutil.rmtree(root)


def test_textbook_seed_reproduces_masks_pixels_labels_and_manifest(corpus):
    a, b = corpus
    for path in a.rglob("*"):
        if path.is_file() and path.name != "data.yaml":
            assert path.read_bytes() == (b / path.relative_to(a)).read_bytes()


def test_textbook_actual_native_boxes_masks_and_text_remain_aligned(corpus):
    root, _ = corpus
    manifest = load_dataset(root)
    assert manifest["origin"] == "synthetic"
    assert len(manifest["records"]) == 16
    standalone = 0
    for row in manifest["records"]:
        assert not row["human_reviewed"] and row["synthetic"]
        assert row["augmentation"]["appearance_profile"] == "textbook"
        stem = Path(row["image"]).stem
        with Image.open(root / row["image"]) as image:
            labels = read_labels(root / row["label"], *image.size)
        objects = json.loads((root / f"objects/{stem}.json").read_text())
        mask = np.array(Image.open(root / f"masks/{stem}.png"))
        assert len(labels) == len(objects)
        for obj, (cls, box) in zip(objects, labels):
            assert NAMES[cls] == obj["class"]
            assert box == pytest.approx(obj["bbox"], abs=2e-6)
            y, x = np.where(mask == obj["mask_index"])
            if len(x):
                assert x.min() >= box[0] - 2e-6 and x.max() < box[2] + 2e-6
                assert y.min() >= box[1] - 2e-6 and y.max() < box[3] + 2e-6
            if obj["id"].startswith("standalone_text_"):
                assert obj["class"] == "text_label"
                standalone += 1
    assert standalone == 16 * 4


def test_resize_preserves_body_contact_and_link_endpoints():
    for source in fixtures().values():
        scene = prepare(variant(source, random.Random(1), False, False), random.Random(2))
        for body in scene.bodies:
            surface = next((s for s in scene.surfaces if s.id == body.on_surface), None)
            if surface:
                a, b = np.array(surface.polyline[0]), np.array(surface.polyline[-1])
                delta = b - a
                distances = [
                    abs(delta[0] * (p[1] - a[1]) - delta[1] * (p[0] - a[0])) / np.linalg.norm(delta)
                    for p in body.mask
                ]
                assert min(distances) < 1e-6
            for link in scene.links:
                for end, index in ((link.a, 0), (link.b, -1)):
                    if end.ref == body.id:
                        assert list(link.polyline[index]) == list(end.point)


def test_filled_objects_own_their_pixels_and_standalone_letters_are_text():
    source = fixtures()["atwood"]
    scene = prepare(variant(source, random.Random(1), True, False), random.Random(2))
    image, objects = render(
        scene,
        random.Random(5),
        style="printed",
        font_size=30,
        font_variant=0,
        arrow_style="open",
        hatch_spacing=16,
        appearance="textbook",
    )
    paper = tuple(int(scene.frame.paper_color[i : i + 2], 16) for i in (1, 3, 5))
    pulley = scene.pulleys[0]
    x, y = map(round, (pulley.center[0] + 7, pulley.center[1] + 13))
    obj = next(o for o in objects if o["id"] == pulley.id)
    assert obj["mask"].getpixel((x, y)) == 255
    assert image.getpixel((x, y)) != paper
    assert (
        len(
            [
                o
                for o in objects
                if o["id"].startswith("standalone_text_") and o["class"] == "text_label"
            ]
        )
        == 4
    )


def test_atwood_enlargement_keeps_bodies_separate():
    source = fixtures()["atwood"]
    for seed in range(24):
        scene = prepare(variant(source, random.Random(seed), False, False), random.Random(seed))
        a, b = sorted(scene.bodies, key=lambda body: body.anchor[0])
        assert a.bbox[2] < b.bbox[0]
        labels = [
            annotation.geometry.bbox
            for annotation in scene.annotations
            if annotation.id in {a.label_ids[0], b.label_ids[0]}
        ]
        assert separate(*labels)
        _, objects = render(
            scene,
            random.Random(seed),
            style="handwritten",
            font_size=36,
            font_variant=1,
            arrow_style="open",
            hatch_spacing=16,
            appearance="textbook",
            handwriting="strong",
        )
        actual = [
            o["mask"].getbbox() for o in objects if o["id"] in {a.label_ids[0], b.label_ids[0]}
        ]
        assert separate(*actual, gap=0)


def test_thick_spring_keeps_space_between_coils():
    source = fixtures()["spring_vertical"]
    _, _, _, scene, _ = sample(
        source,
        ("spring_mass", "handwritten", False, False, False),
        random.Random(73),
        "spring.png",
        appearance="textbook",
    )
    link = next(link for link in scene.links if link.type == "spring")
    length = np.linalg.norm(np.array(link.b.point) - link.a.point)
    assert (length - 24) / link.coils >= scene.frame.stroke_px * 3.5


def test_spring_styles_retain_exact_endpoints_and_different_pixels():
    a, b = [40, 50], [250, 125]
    zigzag = spring_path(a, b, 7, 15, False)
    curved = spring_path(a, b, 7, 15, True)
    assert zigzag[0] == curved[0] == a and zigzag[-1] == curved[-1] == b
    assert len(curved) > len(zigzag) * 4
    dx, dy = b[0] - a[0], b[1] - a[1]
    assert max(
        abs(dx * (p[1] - a[1]) - dy * (p[0] - a[0])) / np.hypot(dx, dy) for p in curved
    ) == pytest.approx(15)


def test_size_audit_scales_exactly_and_keeps_split_counts(corpus):
    root, _ = corpus
    first, second = audit(root, 512), audit(root, 1024)
    assert first["images"] == 16 and first["origin"] == "synthetic"
    for name, row in first["classes"].items():
        assert (
            sum(split[name]["instances"] for split in first["splits"].values()) == row["instances"]
        )
        if row["instances"]:
            for q, size in row["min_side_px_quantiles"].items():
                assert second["classes"][name]["min_side_px_quantiles"][q] == pytest.approx(
                    size * 2
                )
    assert first["classes"]["text_label"]["instances"] >= 16 * 4
    with pytest.raises(ValueError, match="multiple of 32"):
        audit(root, 513)


def test_appearance_profile_is_explicit_and_invalid_names_fail_before_output(corpus):
    root, _ = corpus
    source = fixtures()["pendulum"]
    args = (source, ("pendulum", "printed", False, False, False))
    default = sample(*args, random.Random(23), "sample.png")
    explicit = sample(*args, random.Random(23), "sample.png", appearance="baseline")
    assert default[0].tobytes() == explicit[0].tobytes()
    assert default[4] == explicit[4] and "appearance_profile" not in default[4]
    output = root / "invalid"
    with pytest.raises(ValueError, match="appearance"):
        generate(output, 8, small=True, appearance="unknown")
    assert not output.exists()
