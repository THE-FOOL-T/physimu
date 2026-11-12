import pytest
from circuit_sim.backend.pipeline.values import parse_value, parse_constraints


@pytest.mark.parametrize(
    "text,number,unit",
    [
        ("R1 = 4 Ω", 4, "ohm"),
        ("4Ω", 4, "ohm"),
        ("12 V", 12, "V"),
        ("২Ω", 2, "ohm"),
        ("R₁ = ১০ ওহম", 10, "ohm"),
        ("R_2 = 4.7 kΩ", 4700, "ohm"),
        ("4.7kΩ", 4700, "ohm"),
        ("1MΩ", 1e6, "ohm"),
        ("2mA", 0.002, "A"),
        ("3 µF", 3e-6, "F"),
        ("5uF", 5e-6, "F"),
        ("6μF", 6e-6, "F"),
        ("7nF", 7e-9, "F"),
        ("8pF", 8e-12, "F"),
        ("0.5 H", 0.5, "H"),
        ("১ ভোল্ট", 1, "V"),
        ("২ অ্যাম্পিয়ার", 2, "A"),
        ("৩ ফ্যারাড", 3, "F"),
        ("৪ হেনরি", 4, "H"),
        ("৫ ওয়াট", 5, "W"),
        ("৯ কিলোওহম", 9000, "ohm"),
        ("12 ohm", 12, "ohm"),
        ("13 ohms", 13, "ohm"),
        ("14 volt", 14, "V"),
        ("15 volts", 15, "V"),
        ("16 amp", 16, "A"),
        ("17 amps", 17, "A"),
        ("18 farad", 18, "F"),
        ("19 Ω", 19, "ohm"),
        ("20 KΩ", 20000, "ohm"),
        ("R3=2.2e3 Ω", 2200, "ohm"),
        ("C2=.1 F", 0.1, "F"),
        ("E = 6 V", 6, "V"),
        ("ε = 9V", 9, "V"),
        ("V₁=−3 V", -3, "V"),
        ("r = 1 Ω", 1, "ohm"),
        ("internal resistance 0.5 Ω", 0.5, "ohm"),
        ("R4=০.২৫ Ω", 0.25, "ohm"),
        ("C₁=৪৭ uF", 47e-6, "F"),
        ("১.২mA", 0.0012, "A"),
        ("R5=1e-3 Ω", 0.001, "ohm"),
        ("0 V", 0, "V"),
        ("০Ω", 0, "ohm"),
        ("3 kn", 3000, "ohm"),
        ("8 ko", 8000, "ohm"),
        ("2Ko", 2000, "ohm"),
        ("R1 = 10 Q", 10, "ohm"),
        ("R2 = 20 9", 20, "ohm"),
        ("R3 = 10 Q", 10, "ohm"),
        ("R4 = 10 O", 10, "ohm"),
        ("R5 = 100 q", 100, "ohm"),
    ],
)
def test_parse_si(text, number, unit):
    result = parse_value(text)
    assert result["number"] == pytest.approx(number)
    assert result["unit"] == unit


@pytest.mark.parametrize("text", ["R1", "R₁", "R_1", "R2 = ?", "find x", "?"])
def test_unknowns(text):
    assert parse_value(text)["number"] is None


def test_measurements_and_ratio():
    cs = parse_constraints("I(R3) = 2 A; voltage across R1 is 6 V; R1/R2 = 3")
    assert [(c.type, c.target, c.value) for c in cs] == [
        ("current", "R3", 2),
        ("voltage", "R1", 6),
        ("ratio", "R1/R2", 3),
    ]
