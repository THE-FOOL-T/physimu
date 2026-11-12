import copy

import cv2
import numpy as np
import pytest

from circuit_sim.backend.pipeline.netlist import (
    Component,
    Terminal,
    Value,
    Netlist,
    Image,
)
from circuit_sim.backend.pipeline.validate import validate, safe_solve
from circuit_sim.backend.pipeline.wires import prepare_trace, trace
from circuit_sim.backend.pipeline.wire_geometry import terminal_hit
from circuit_sim.backend.pipeline.wire_repair import prune_spurs


def diagram(gap=0, arrow=False):
    image = np.full((240, 360, 3), 255, np.uint8)
    for path in [
        [(100, 50), (40, 50), (40, 180), (200, 180)],
        [(140, 50), (300, 50), (300, 180), (220, 180)],
    ]:
        cv2.polylines(image, [np.array(path)], False, (0, 0, 0), 2)
    cv2.rectangle(image, (100, 42), (140, 58), (0, 0, 0), 2)
    cv2.line(image, (200, 166), (200, 194), (0, 0, 0), 2)
    cv2.line(image, (220, 173), (220, 187), (0, 0, 0), 2)
    if gap:
        image[100 : 100 + gap, 37:44] = 255
    marks = []
    if arrow:
        cv2.arrowedLine(image, (245, 50), (280, 50), (0, 0, 0), 2, tipLength=0.25)
        marks = [{"type": "arrow", "bbox": [242, 38, 284, 62]}]
    cs = []
    for id_, kind, bbox, a, b, value, unit in [
        ("R1", "resistor", (100, 42, 140, 58), (100, 50), (140, 50), 100, "ohm"),
        ("V1", "dc_source", (195, 164, 225, 196), (195, 180), (225, 180), 3, "V"),
    ]:
        cs.append(
            Component(
                id=id_,
                type=kind,
                bbox=bbox,
                terminals=[
                    Terminal(id=id_ + ".a", node="pending", xy=a),
                    Terminal(id=id_ + ".b", node="pending", xy=b),
                ],
                value=Value(number=value, unit=unit, status="given", source="ocr"),
            )
        )
    return image, cs, marks


@pytest.mark.parametrize("gap", [0, 4, 8, 12])
def test_scaled_gap_repair_closes_a_real_two_part_loop(gap):
    image, cs, marks = diagram(gap)
    diagnostic = {}
    nodes, graph, warnings = trace(image, cs, annotations=marks, diagnostics=diagnostic)
    net = validate(
        Netlist(
            image=Image(width=360, height=240),
            components=cs,
            nodes=nodes,
            wire_graph=graph,
        )
    )
    _, solution = safe_solve(net)
    assert len(nodes) == 2
    assert abs(solution["components"]["R1"]["current"]) == pytest.approx(0.03)
    assert not any(w.code == "no_closed_loop" for w in net.warnings)
    assert diagnostic["terminals_snapped"] == 4 and diagnostic["terminals_floating"] == 0
    if gap >= 4:
        assert ("gap_bridged", None) in warnings


def test_arrow_and_padded_ocr_box_do_not_cut_the_wire():
    image, cs, marks = diagram(arrow=True)
    texts = [{"text": "10 Q", "bbox": [240, 35, 287, 54], "confidence": 0.9}]
    nodes, graph, _ = trace(image, cs, texts, marks)
    net = validate(Netlist(components=cs, nodes=nodes, wire_graph=graph))
    assert len(nodes) == 2
    assert not any(w.code == "no_closed_loop" for w in net.warnings)


def test_snap_rejects_a_nearby_parallel_wire():
    a = Terminal(id="a", xy=(100, 100), node="pending")
    b = Terminal(id="b", xy=(150, 100), node="pending")
    candidates = np.array([[x, 110] for x in range(75, 100)], float)
    assert terminal_hit(a, b, candidates, 30, 2) is None
    candidates = np.vstack((candidates, [80, 100]))
    assert terminal_hit(a, b, candidates, 30, 2)[0] == (80, 100)


def test_loose_detector_box_refines_axis_and_keeps_inside_lead_stubs():
    image, cs, marks = diagram()
    cs[0].bbox = (91, 37, 151, 67)
    cs[0].terminals[0].xy = (91, 52)
    cs[0].terminals[1].xy = (151, 52)
    prepare_trace(image, cs, annotations=marks)
    assert cs[0].terminals[0].xy[1] == pytest.approx(50, abs=1)
    assert cs[0].terminals[0].xy[0] > 95
    assert cs[0].terminals[1].xy[0] < 146


def test_short_skeleton_spur_is_pruned_without_cutting_main_wire():
    points = [(x, 20) for x in range(5, 36)] + [(20, y) for y in (21, 22, 23)]
    adj = {p: {q for q in points if abs(p[0] - q[0]) + abs(p[1] - q[1]) == 1} for p in points}
    prune_spurs(adj, 2, [])
    assert (20, 23) not in adj and (20, 20) in adj
    assert len(adj[(20, 20)]) == 2


def test_detected_dot_overrides_pixel_only_crossing_decision():
    from circuit_sim.backend.tests.test_wires import cross

    image, cs = cross()
    trace(image, cs, annotations=[{"type": "junction", "bbox": [96, 96, 104, 104]}])
    assert cs[0].terminals[1].node == cs[2].terminals[1].node


def test_disconnected_detections_remain_visible_and_dead_source_is_partial():
    image, cs, marks = diagram()
    image[90:140, 37:44] = 255
    nodes, graph, _ = trace(image, cs, annotations=marks)
    net = validate(Netlist(components=cs, nodes=nodes, wire_graph=graph))
    assert not any(c.disabled for c in net.components)
    assert net.meta.provenance == "partial"
    assert any(w.code == "source_open_loop" and w.ref == "V1" for w in net.warnings)


def test_solver_failure_keeps_observed_geometry_instead_of_a_demo(monkeypatch):
    from circuit_sim.backend.pipeline import validate as module

    image, cs, marks = diagram()
    nodes, graph, _ = trace(image, cs, annotations=marks)
    net = Netlist(components=cs, nodes=nodes, wire_graph=graph)
    original = copy.deepcopy(net.components)
    monkeypatch.setattr(
        module,
        "solve",
        lambda *a, **k: (_ for _ in ()).throw(ValueError("test failure")),
    )
    result, solution = module.safe_solve(net)
    assert result.components == original and result.meta.provenance == "partial"
    assert any(w["code"] == "solve_failed" for w in solution["warnings"])


def test_ray_repairs_a_t_contact_without_jumping_over_first_wire():
    image, cs, marks = diagram()
    # Two independently retained strokes; the ray reaches the first vertical.
    from circuit_sim.backend.pipeline.wire_repair import repair_gaps

    pixels = (
        [(x, 40) for x in range(5, 26)]
        + [(35, y) for y in range(20, 61)]
        + [(45, y) for y in range(20, 61)]
    )
    adj = {p: {q for q in pixels if abs(p[0] - q[0]) + abs(p[1] - q[1]) == 1} for p in pixels}
    warnings, _ = repair_gaps(adj, cs, np.zeros((80, 80), np.uint8), 2)
    assert ("gap_bridged", None) in warnings
    assert any(q[0] == 35 for q in adj[(25, 40)])
    assert not any(q[0] == 45 for q in adj[(25, 40)])


def test_symbol_sized_gap_is_a_ghost_suggestion_instead_of_a_wire():
    image, cs, marks = diagram()
    image[90:135, 37:44] = 255
    prepared = prepare_trace(image, cs)
    assert prepared["ghosts"]
    assert prepared["ghosts"][0]["reason"] == "missing_part"
