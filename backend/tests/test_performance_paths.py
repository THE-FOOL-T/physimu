import copy
import cv2
import numpy as np
from circuit_sim.backend.pipeline.netlist import Component, Terminal
from circuit_sim.backend.pipeline import wires
from circuit_sim.backend.pipeline.retry import recover


def part():
    return Component(
        id="R1",
        type="resistor",
        bbox=(0, 0, 0, 0),
        terminals=[
            Terminal(id="a", node="pending", xy=(20, 100)),
            Terminal(id="b", node="pending", xy=(380, 100)),
        ],
    )


def test_snap_retries_reuse_skeleton_without_mutating_cached_graph(monkeypatch):
    image = np.full((200, 400, 3), 255, np.uint8)
    cv2.line(image, (20, 100), (380, 100), (0, 0, 0), 2)
    calls = 0
    original = wires.skeletonize

    def counted(*args, **kwargs):
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(wires, "skeletonize", counted)
    prepared = wires.prepare_trace(image, [part()])
    before = copy.deepcopy(prepared["adj"])
    for snap in [1, 1.5, 0.7]:
        wires.trace(image, [part()], snap_scale=snap, prepared=prepared)
    assert calls == 1
    assert prepared["adj"] == before


def test_detector_retries_are_bounded_crops_with_global_coordinates():
    image = np.full((1800, 1800, 3), 255, np.uint8)
    c = part()
    c.bbox = (800, 800, 850, 850)
    shapes = []

    def detector(crop, **kwargs):
        shapes.append(crop.shape[:2])
        assert not kwargs["tiled"]
        item = part()
        item.bbox = (300, 300, 330, 330)
        item.terminals[0].xy = (300, 315)
        item.terminals[1].xy = (330, 315)
        return [item], []

    recovered, _ = recover(image, [c], [], detector)
    assert shapes and all(max(shape) <= 512 for shape in shapes)
    assert len({item.id for item in recovered}) == len(recovered)
    assert recovered[-1].bbox[0] >= 500
