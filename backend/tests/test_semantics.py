import json
from pathlib import Path
import cv2
import numpy as np
import pytest
from circuit_sim.backend.pipeline.values import parse_value, parse_constraints
from circuit_sim.backend.pipeline.netlist import (
    Netlist,
    Constraint,
    Component,
    Terminal,
)
from circuit_sim.backend.pipeline.resolve import resolve
from circuit_sim.backend.pipeline.associate import associate
from circuit_sim.backend.pipeline.annotations import dashed_mask


@pytest.mark.parametrize(
    "prefix,factor", [("মিলি", 1e-3), ("মাইক্রো", 1e-6), ("কিলো", 1e3), ("মেগা", 1e6)]
)
@pytest.mark.parametrize(
    "unit,expected",
    [("ওহম", "ohm"), ("অ্যাম্পিয়ার", "A"), ("ভোল্ট", "V"), ("ফ্যারাড", "F"), ("ওয়াট", "W")],
)
def test_bangla_si_prefix_words(prefix, factor, unit, expected):
    result = parse_value("২ " + prefix + " " + unit)
    assert result["number"] == pytest.approx(2 * factor)
    assert result["unit"] == expected


@pytest.mark.parametrize(
    "text,kind,target,value",
    [
        ("equivalent resistance is 5 Ω", "equivalent_resistance", "total", 5),
        ("R_eq = 5Ω", "equivalent_resistance", "total", 5),
        ("তুল্য রোধ ৫ Ω", "equivalent_resistance", "total", 5),
        ("তুল্য রোধ = ২ কিলোওহম", "equivalent_resistance", "total", 2000),
        ("V_AB = 6 V", "voltage", "A-B", 6),
        ("V_PQ = ২ মিলিভোল্ট", "voltage", "P-Q", 0.002),
        ("potential difference between A and B is 6 V", "voltage", "A-B", 6),
        ("voltage between P and Q = 12 V", "voltage", "P-Q", 12),
        ("A ও B এর বিভব পার্থক্য ৬ V", "voltage", "A-B", 6),
        ("P ও Q এর বিভব পার্থক্য = ২ ভোল্ট", "voltage", "P-Q", 2),
        ("total power = 24 W", "power", "total", 24),
        ("মোট ক্ষমতা ২ কিলোওয়াট", "power", "total", 2000),
        ("total current is 2 A", "current", "total", 2),
        ("মোট প্রবাহ ৫ মিলিঅ্যাম্পিয়ার", "current", "total", 0.005),
        ("R_eq: 2.2 kΩ", "equivalent_resistance", "total", 2200),
        ("total power is 2 mW", "power", "total", 0.002),
    ],
)
def test_extended_measurements(text, kind, target, value):
    result = parse_constraints(text)
    assert len(result) == 1
    assert result[0].type == kind and result[0].target == target
    assert result[0].value == pytest.approx(value)


@pytest.mark.parametrize(
    "text",
    [
        "find R1",
        "determine R2",
        "find C₁",
        "determine L2",
        "R3 কত",
        "R₄ নির্ণয় কর",
        "R5 বের কর",
        "unknown R6",
    ],
)
def test_find_markers(text):
    result = parse_value(text)
    assert result["unknown"] and result["number"] is None


@pytest.mark.parametrize(
    "kind,target,value",
    [
        ("equivalent_resistance", "total", 12),
        ("voltage", "A-B", 8),
        ("power", "total", 12),
        ("current", "total", 1),
    ],
)
@pytest.mark.parametrize("state", ["determined", "underdetermined", "inconsistent"])
def test_new_resolver_measurements(kind, target, value, state):
    net = Netlist.model_validate(
        json.loads((Path(__file__).resolve().parents[2] / "fixtures/series.json").read_text())[
            "netlist"
        ]
    )
    for n in net.nodes:
        if n.id == "m":
            n.label = "A"
        if n.id == "g":
            n.label = "B"
    net.components[1].value.number = None
    if state == "underdetermined":
        net.components[2].value.number = None
    net.constraints = [Constraint(type=kind, target=target, value=value)]
    if state == "inconsistent":
        net.constraints.append(Constraint(type=kind, target=target, value=value * 2))
    result = resolve(net)
    if state == "determined":
        assert result.components[1].value.status == "solved"
        assert result.components[1].value.number == pytest.approx(4, rel=1e-5)
    else:
        assert result.components[1].value.status == "assumed"
    if state == "inconsistent":
        assert any(w.code == "inconsistent_constraints" for w in result.warnings)


def component(id_, x, y=100):
    return Component(
        id=id_,
        type="resistor",
        bbox=(x - 20, y - 10, x + 20, y + 10),
        terminals=[
            Terminal(id=id_ + ".a", xy=(x - 20, y), node="a"),
            Terminal(id=id_ + ".b", xy=(x + 20, y), node="b"),
        ],
    )


def test_global_assignment_avoids_greedy_conflict_and_preserves_name_value_pairs():
    cs = [component("R1", 100), component("R2", 200)]
    texts = [
        {"text": "10 Ω", "bbox": [135, 65, 145, 75], "confidence": 0.99},
        {"text": "4 Ω", "bbox": [95, 65, 105, 75], "confidence": 0.9},
        {"text": "R1", "bbox": [95, 45, 105, 55], "confidence": 0.9},
        {"text": "R2", "bbox": [195, 45, 205, 55], "confidence": 0.9},
    ]
    associate(cs, texts)
    assert [(c.label, c.value.number) for c in cs] == [("R1", 4), ("R2", 10)]


@pytest.mark.parametrize("dotted", [False, True])
def test_periodic_annotations_removed_without_erasing_real_crossing_wire(dotted):
    binary = np.zeros((150, 240), np.uint8)
    for x in range(15, 215, 12):
        cv2.line(binary, (x, 40), (x + (2 if dotted else 7), 40), 255, 2)
    cv2.line(binary, (10, 100), (225, 100), 255, 2)
    cv2.line(binary, (100, 15), (100, 120), 255, 2)
    mask = dashed_mask(binary)
    cleaned = binary.copy()
    cleaned[mask > 0] = 0
    assert np.count_nonzero(cleaned[38:43, 15:215]) < np.count_nonzero(binary[38:43, 15:215]) * 0.25
    assert np.all(cleaned[100, 10:225] > 0)
    assert np.all(cleaned[15:120, 100] > 0)
