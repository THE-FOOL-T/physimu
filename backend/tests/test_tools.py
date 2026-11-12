import json
from pathlib import Path
import pytest
from circuit_sim.backend.tools.make_synthetic import generate
from circuit_sim.backend.pipeline.netlist import Netlist
from circuit_sim.backend.solver.mna import solve
from circuit_sim.backend.tools.eval_detector import ap101, iou, evaluate


def test_synthetic_geometry_labels_and_electrical_balance():
    for seed in [0, 1, 2, 7]:
        image, net, boxes = generate(seed, hand_drawn=bool(seed % 2), bangla=True)
        Netlist.model_validate(net.as_dict())
        assert len(boxes) == len(net.components)
        assert image.size == (net.image.width, net.image.height)
        result = solve(net)
        assert result["invariants"]["relative_power_error"] < 1e-9
        for s in net.wire_graph.segments:
            a = next(p for p in net.wire_graph.points if p.id == s.from_)
            b = next(p for p in net.wire_graph.points if p.id == s.to)
            assert s.polyline[0] == a.xy and s.polyline[-1] == b.xy


def test_detector_ap_math_including_missing_class():
    assert iou([0, 0, 10, 10], [0, 0, 10, 10]) == 1
    assert ap101([1, 1], [0, 0], 2) == 1
    assert ap101([], [], 3) == 0
    assert ap101([], [], 0) is None


def test_reference_class_mapping_and_unemittted_meter_recall(tmp_path):
    from types import SimpleNamespace
    import numpy as np
    from PIL import Image

    images = tmp_path / "images"
    labels = tmp_path / "labels"
    images.mkdir()
    labels.mkdir()
    Image.new("RGB", (100, 100), "white").save(images / "x.png")
    (labels / "x.txt").write_text("0 .25 .25 .2 .2\n2 .75 .75 .2 .2\n")
    box = SimpleNamespace(
        cls=np.array([1]), conf=np.array([0.9]), xyxy=np.array([[15, 15, 35, 35]])
    )
    model = SimpleNamespace(
        names={0: "resistor", 1: "ammeter"},
        predict=lambda *a, **k: [SimpleNamespace(boxes=[box])],
    )
    result = evaluate(
        model, images, labels, class_names={0: "ammeter", 1: "resistor", 2: "voltmeter"}
    )
    assert result["classes"]["ammeter"]["recall_conf025"] == 1
    assert result["classes"]["voltmeter"]["recall_conf025"] == 0
