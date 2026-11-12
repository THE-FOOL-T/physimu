import math
import pytest

from circuit_sim.backend.pipeline.associate import associate
from circuit_sim.backend.pipeline.netlist import Component, Terminal, Value, Polarity


def make_component(
    id_,
    kind,
    x,
    y=100,
    width=40,
    height=20,
    unit=None,
    polarity=False,
    orientation_deg=0.0,
    terminals=None,
):
    default_unit = {
        "resistor": "ohm",
        "rheostat": "ohm",
        "potentiometer": "ohm",
        "dc_source": "V",
        "battery": "V",
        "ac_source": "V",
        "capacitor": "F",
        "inductor": "H",
        "current_source": "A",
    }.get(kind, "ohm")

    if terminals is None:
        if orientation_deg == 90.0 or height > width:
            terminals = [
                Terminal(id=id_ + ".a", xy=(x, y - height / 2), node="a"),
                Terminal(id=id_ + ".b", xy=(x, y + height / 2), node="b"),
            ]
        else:
            terminals = [
                Terminal(id=id_ + ".a", xy=(x - width / 2, y), node="a"),
                Terminal(id=id_ + ".b", xy=(x + width / 2, y), node="b"),
            ]

    return Component(
        id=id_,
        type=kind,
        bbox=(x - width / 2, y - height / 2, x + width / 2, y + height / 2),
        orientation_deg=orientation_deg,
        terminals=terminals,
        value=Value(unit=unit or default_unit),
        polarity=Polarity(positive_terminal=id_ + ".a") if polarity else None,
    )


def text(value, x, y=60, confidence=0.95, width=30, height=12, **extra):
    return {
        "text": value,
        "bbox": [x - width / 2, y - height / 2, x + width / 2, y + height / 2],
        "confidence": confidence,
        **extra,
    }


def test_combined_reference_and_value_stay_on_one_component():
    components = [make_component("R1", "resistor", 100), make_component("R2", "resistor", 240)]
    texts = [text("R1 = 100 Ω", 100)]
    result = associate(components, texts)

    assert components[0].label == "R1"
    assert components[0].value.number == pytest.approx(100)
    assert components[1].label is None
    assert components[1].value.number is None
    assert result["matched"][0]["role"] == "combined"
    assert texts[0]["association"]["component_id"] == "R1"


def test_two_nearby_resistors():
    # Two resistors spaced closely; each gets its corresponding label and value
    components = [make_component("R1", "resistor", 100), make_component("R2", "resistor", 180)]
    texts = [
        text("R1", 100, y=55),
        text("100 Ω", 100, y=40),
        text("R2", 180, y=55),
        text("220 Ω", 180, y=40),
    ]
    associate(components, texts)

    assert components[0].label == "R1"
    assert components[0].value.number == pytest.approx(100)
    assert components[1].label == "R2"
    assert components[1].value.number == pytest.approx(220)


def test_global_assignment_resolves_greedy_collision():
    components = [make_component("R1", "resistor", 100), make_component("R2", "resistor", 200)]
    texts = [
        {"text": "10 Ω", "bbox": [135, 65, 145, 75], "confidence": 0.99},
        {"text": "4 Ω", "bbox": [95, 65, 105, 75], "confidence": 0.9},
        {"text": "R1", "bbox": [95, 45, 105, 55], "confidence": 0.9},
        {"text": "R2", "bbox": [195, 45, 205, 55], "confidence": 0.9},
    ]
    associate(components, texts)

    assert [(c.label, c.value.number) for c in components] == [("R1", 4), ("R2", 10)]


def test_incorrect_nearest_centre_matches():
    # Long vertical resistor R1 and small square resistor R2.
    # Text is placed close to R1's top edge, making its distance to R1's center larger
    # than to R2's center, but box_gap and axial alignment favor R1.
    r1 = make_component("R1", "resistor", x=100, y=100, width=20, height=80, orientation_deg=90)
    r2 = make_component("R2", "resistor", x=140, y=65, width=20, height=20)
    label_text = text("R1", 100, y=55, width=20, height=10)

    # Center of R1 is (100, 100), center of label is (100, 55) -> dist = 45
    # Center of R2 is (140, 65), center of label is (100, 55) -> dist = sqrt(40^2 + 10^2) = 41.2
    # Greedy center matching would wrongly pick R2!
    associate([r1, r2], [label_text])

    assert r1.label == "R1"
    assert r2.label is None


def test_horizontal_and_vertical_components():
    r_horiz = make_component("R1", "resistor", x=100, y=100, width=50, height=20, orientation_deg=0)
    r_vert = make_component("R2", "resistor", x=200, y=100, width=20, height=50, orientation_deg=90)

    texts = [
        text("R1", 100, y=65),
        text("47 Ω", 100, y=45),
        text("R2", 230, y=100),
        text("68 Ω", 250, y=100),
    ]
    associate([r_horiz, r_vert], texts)

    assert (r_horiz.label, r_horiz.value.number) == ("R1", 47)
    assert (r_vert.label, r_vert.value.number) == ("R2", 68)


def test_rotated_components():
    # Rotated component at 45 degrees
    x, y, d = 150.0, 150.0, 30.0
    rad = math.radians(45)
    dx, dy = d * math.cos(rad), d * math.sin(rad)
    terminals = [
        Terminal(id="R1.a", xy=(x - dx, y - dy), node="a"),
        Terminal(id="R1.b", xy=(x + dx, y + dy), node="b"),
    ]
    r_rot = make_component(
        "R1", "resistor", x=x, y=y, width=40, height=40, orientation_deg=45.0, terminals=terminals
    )

    # Place text perpendicular to the 45-degree axis (along normal: -sin(45), cos(45))
    nx, ny = -25 * math.sin(rad), 25 * math.cos(rad)
    label_text = text("R1", x + nx, y + ny)
    val_text = text("330 Ω", x + nx - 10, y + ny + 10)

    associate([r_rot], [label_text, val_text])

    assert r_rot.label == "R1"
    assert r_rot.value.number == pytest.approx(330)


def test_multiple_text_labels_belonging_to_one_component():
    # A single resistor receives both reference label and value from two separate texts
    component = make_component("R1", "resistor", 100)
    texts = [
        text("R1", 100, y=55),
        text("1 kΩ", 100, y=35),
    ]
    associate([component], texts)

    assert component.label == "R1"
    assert component.value.number == pytest.approx(1000)
    assert component.value.unit == "ohm"


def test_conflicting_candidate_assignments():
    # Two values competing for one resistor: closer, higher-confidence value wins
    r = make_component("R1", "resistor", 100)
    texts = [
        text("10 Ω", 100, y=60, confidence=0.95),
        text("20 Ω", 100, y=30, confidence=0.70),
    ]
    result = associate([r], texts)

    assert r.value.number == pytest.approx(10)
    assert len(result["matched"]) == 1
    assert result["matched"][0]["text"] == "10 Ω"


def test_reference_prefix_filters_wrong_component_type():
    components = [
        make_component("R1", "resistor", 100),
        make_component("C1", "capacitor", 135),
    ]
    labels = [text("C1", 95)]
    associate(components, labels)

    assert components[0].label is None
    assert components[1].label == "C1"


def test_physical_unit_filters_wrong_component_type():
    components = [
        make_component("R1", "resistor", 100),
        make_component("V1", "dc_source", 135),
    ]
    values = [text("6 V", 95)]
    associate(components, values)

    assert components[0].value.number is None
    assert components[1].value.number == pytest.approx(6)
    assert components[1].value.unit == "V"


def test_incorrect_unit_component_combinations():
    # Capacitance unit near resistor and resistance unit near capacitor
    r = make_component("R1", "resistor", 100)
    c = make_component("C1", "capacitor", 200)
    texts = [
        text("10 µF", 100, y=60),  # near R1, but F is for capacitor
        text("470 Ω", 200, y=60),  # near C1, but ohm is for resistor
    ]
    associate([r, c], texts)

    # Neither should accept the wrong unit
    assert r.value.number is None
    assert c.value.number is None


def test_ambiguous_midpoint_is_left_unassigned():
    components = [make_component("R1", "resistor", 100), make_component("R2", "resistor", 160)]
    texts = [text("10 Ω", 130)]
    result = associate(components, texts)

    assert all(c.value.number is None for c in components)
    assert result["unmatched"][0]["reason"] == "ambiguous"


def test_ambiguous_combined_text_is_never_split_between_components():
    components = [make_component("R1", "resistor", 100), make_component("R2", "resistor", 160)]
    texts = [text("R1 = 10 Ω", 130)]
    result = associate(components, texts)

    assert all(c.label is None and c.value.number is None for c in components)
    assert result["unmatched"][0]["role"] == "name_value"


def test_separate_name_and_value_prefer_same_side_of_component():
    components = [make_component("R1", "resistor", 100), make_component("R2", "resistor", 250)]
    texts = [
        text("R1", 100, y=55),
        text("10 Ω", 100, y=35),
        text("R2", 250, y=55),
        text("20 Ω", 250, y=35),
    ]
    associate(components, texts)

    assert [(c.label, c.value.number) for c in components] == [("R1", 10), ("R2", 20)]


def test_unitless_number_requires_high_ocr_confidence():
    low_conf = [make_component("R1", "resistor", 100)]
    associate(low_conf, [text("100", 100, confidence=0.6)])
    assert low_conf[0].value.number is None

    high_conf = [make_component("R1", "resistor", 100)]
    associate(high_conf, [text("100", 100, confidence=0.96)])
    assert high_conf[0].value.number == pytest.approx(100)


def test_missing_or_unparseable_ocr_values():
    component = make_component("R1", "resistor", 100)
    unparseable = [
        text("random text label", 100, y=60),
        text("---", 100, y=50),
        text("...", 100, y=40),
    ]
    result = associate([component], unparseable)

    assert component.label is None
    assert component.value.number is None
    assert len(result["matched"]) == 0


def test_user_value_is_never_overwritten():
    component = make_component("R1", "resistor", 100)
    component.value = Value(number=220, unit="ohm", status="user", source="user", confidence=1)
    associate([component], [text("100 Ω", 100)])

    assert component.value.number == pytest.approx(220)
    assert component.value.status == "user"


def test_internal_resistance_only_attaches_to_source():
    components = [
        make_component("R1", "resistor", 100),
        make_component("V1", "dc_source", 135),
    ]
    texts = [text("internal resistance 2 Ω", 95)]
    associate(components, texts)

    assert components[0].internal_resistance is None
    assert components[1].internal_resistance == pytest.approx(2)


def test_plus_and_minus_markers_resolve_source_polarity_by_terminal():
    source = make_component("V1", "dc_source", 100, polarity=True)
    texts = [
        {"text": "+", "bbox": [75, 95, 85, 105], "confidence": 0.95},
        {"text": "-", "bbox": [115, 95, 125, 105], "confidence": 0.95},
    ]
    result = associate([source], texts)

    assert source.polarity.positive_terminal == "V1.a"
    assert [m["role"] for m in result["matched"]] == ["polarity", "polarity"]


def test_empty_inputs_are_safe():
    assert associate([], [text("10 Ω", 100)])["matched"] == []
    assert associate([make_component("R1", "resistor", 100)], [])["matched"] == []


def test_randomized_synthetic_layouts_exceed_90_percent_assignment_coverage():
    import random

    rng = random.Random(314159)
    total = assigned = correct = wrong = 0

    for _ in range(120):
        count = rng.randint(2, 6)
        xs = []
        x = 100
        for _index in range(count):
            x += rng.randint(65, 115)
            xs.append(x)

        components = []
        texts = []
        for index, x in enumerate(xs):
            ref = f"R{index + 1}"
            width = rng.randint(30, 52)
            height = rng.randint(16, 28)
            components.append(
                Component(
                    id=ref,
                    type="resistor",
                    bbox=(x - width / 2, 100 - height / 2, x + width / 2, 100 + height / 2),
                    terminals=[
                        Terminal(id=ref + ".a", xy=(x - width / 2, 100), node="a"),
                        Terminal(id=ref + ".b", xy=(x + width / 2, 100), node="b"),
                    ],
                    value=Value(unit="ohm"),
                )
            )

            for role in ("label", "value"):
                jitter_x = rng.randint(-18, 18)
                y = 100 + rng.choice((-1, 1)) * rng.randint(18, 60) + rng.randint(-8, 8)
                if role == "label":
                    recognized = ref
                    text_width = rng.randint(12, 30)
                else:
                    recognized = f"{rng.choice((10, 22, 47, 100, 220, 470, 1000))} Ω"
                    text_width = rng.randint(20, 45)
                texts.append(
                    {
                        "text": recognized,
                        "bbox": [
                            x + jitter_x - text_width / 2,
                            y - 6,
                            x + jitter_x + text_width / 2,
                            y + 6,
                        ],
                        "confidence": rng.uniform(0.78, 0.99),
                        "target_component": ref,
                    }
                )

        associate(components, texts)
        for item in texts:
            total += 1
            link = item.get("association")
            if link:
                assigned += 1
                if link["component_id"] == item["target_component"]:
                    correct += 1
                else:
                    wrong += 1

    assert total > 500
    assert assigned / total >= 0.90
    assert wrong == 0
    assert correct / total >= 0.90
