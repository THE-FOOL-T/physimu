from pathlib import Path
from PIL import Image
import pytest
from circuit_sim.backend.tools.leakage import check_frozen, balanced_records
from circuit_sim.backend.tools.make_synthetic import generate


def test_reencoded_frozen_image_is_rejected(tmp_path):
    from PIL import ImageDraw

    image = Image.new("RGB", (200, 200), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 30, 160, 170), outline="black", width=4)
    first = tmp_path / "test.png"
    other = tmp_path / "train.jpg"
    image.save(first)
    image.save(other, quality=95)
    assert check_frozen([other], [first])


def test_synthetic_fraction_cap_oversamples_real():
    records = [{"synthetic": False, "id": 0}] + [{"synthetic": True, "id": i} for i in range(5)]
    balanced = balanced_records(records)
    assert len(balanced) == 10
    assert sum(r["synthetic"] for r in balanced) == 5
    with pytest.raises(ValueError):
        balanced_records([{"synthetic": True}])


def test_orientation_classifier_stays_disabled_without_real_evidence(tmp_path):
    import json
    import numpy as np
    from circuit_sim.backend.pipeline.orientation import classify, features

    crop = np.full((40, 60, 3), 255, np.uint8)
    model = tmp_path / "model.npz"
    report = tmp_path / "report.json"
    np.savez(model, centroids=np.array([features(crop)]), labels=np.array([3]))
    report.write_text(
        json.dumps(
            {
                "real_test_count": 0,
                "classifier_accuracy": None,
                "heuristic_accuracy": None,
            }
        )
    )
    assert classify(crop, model, report) is None
    report.write_text(
        json.dumps(
            {
                "real_test_count": 20,
                "classifier_accuracy": 0.7,
                "heuristic_accuracy": 0.8,
            }
        )
    )
    assert classify(crop, model, report) is None
    report.write_text(
        json.dumps(
            {
                "real_test_count": 20,
                "classifier_accuracy": 0.9,
                "heuristic_accuracy": 0.8,
            }
        )
    )
    assert classify(crop, model, report)["orientation_deg"] == 90


def test_smoke_or_regressed_detectors_cannot_be_selected():
    import copy
    from circuit_sim.backend.tools.compare_detectors import eligible

    names = [
        "resistor",
        "voltage_source",
        "capacitor",
        "switch",
        "ammeter",
        "voltmeter",
    ]
    baseline = {
        "count": 99,
        "classes": {name: {"recall_conf025": 0.5} for name in names},
    }
    candidate = copy.deepcopy(baseline)
    for row in candidate["classes"].values():
        row["recall_conf025"] = 0.6
    assert eligible(baseline, candidate)
    candidate["split"] = "1-epoch smoke"
    assert not eligible(baseline, candidate)
    candidate["split"] = "frozen"
    candidate["classes"]["resistor"]["recall_conf025"] = 0.47
    assert not eligible(baseline, candidate)


def test_all_symbol_classes_and_augmented_geometry():
    import yaml

    names = yaml.safe_load(
        (Path(__file__).resolve().parents[2] / "data/class_schema.yaml").read_text()
    )["names"]
    classes = set()
    for seed in range(16):
        image, net, boxes = generate(
            seed, hand_drawn=True, bangla=True, all_classes=True, augment_scene=True
        )
        net.references()
        classes.update(cls for cls, _ in boxes)
        for _, (x, y, x2, y2) in boxes:
            assert 0 <= x < x2 <= image.width and 0 <= y < y2 <= image.height
        for s in net.wire_graph.segments:
            assert s.polyline[0] == next(p.xy for p in net.wire_graph.points if p.id == s.from_)
            assert s.polyline[-1] == next(p.xy for p in net.wire_graph.points if p.id == s.to)
    assert classes == set(range(len(names)))
