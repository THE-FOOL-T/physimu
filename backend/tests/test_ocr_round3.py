import unicodedata
import cv2
import numpy as np
import pytest
from circuit_sim.backend.pipeline.values import parse_value
from circuit_sim.backend.pipeline.netlist import Component, Terminal, Value
from circuit_sim.backend.pipeline.associate import associate
from circuit_sim.backend.pipeline.ocr_regions import (
    clean_strokes,
    paragraph_text,
    crop_variants,
)


def part(kind="resistor", id_="R1"):
    return Component(
        id=id_,
        type=kind,
        bbox=(90, 95, 150, 115),
        terminals=[
            Terminal(id=id_ + ".a", xy=(90, 105), node="a"),
            Terminal(id=id_ + ".b", xy=(150, 105), node="b"),
        ],
    )


@pytest.mark.parametrize(
    "text,number,unit",
    [
        ("40 Ohm", 40, "ohm"),
        ("40 OHMS", 40, "ohm"),
        ("3.0 v", 3, "V"),
        ("1OO Ω", 100, "ohm"),
        ("l0 Ω", 10, "ohm"),
        ("1S Ω", 15, "ohm"),
        ("1B Ω", 18, "ohm"),
        ("4,7 kΩ", 4700, "ohm"),
        ("4 0 Ω", 40, "ohm"),
        ("5 µF", 5e-6, "F"),
        ("5 uF", 5e-6, "F"),
        ("5 pF", 5e-12, "F"),
        ("20 Ω", 20, "ohm"),
    ],
)
def test_tolerant_explicit_values_preserve_real_prefixes(text, number, unit):
    result = parse_value(text)
    assert result["number"] == pytest.approx(number)
    assert result["unit"] == unit


@pytest.mark.parametrize("suffix", ["Q", "O", "0", "2", "S2", "n", "9", "52"])
def test_ohm_lookalikes_require_resistance_context(suffix):
    text = "40 " + suffix
    plain = parse_value(text)
    assert plain is None or plain["unit"] is None
    contextual = parse_value(text, "resistor")
    assert contextual["number"] == 40 and contextual["unit"] == "ohm"
    assert contextual["unit_inferred"] and contextual["confidence"] <= 0.6


@pytest.mark.parametrize("text", ["E", "ε", "K", "S", "G", "I"])
def test_false_bare_names_never_label_a_resistor(text):
    c = part()
    items = [{"text": text, "bbox": [100, 65, 130, 85], "confidence": 0.99}]
    associate([c], items)
    assert c.label is None
    assert c.value.number is None


@pytest.mark.parametrize(
    "kind,text,number,unit",
    [
        ("resistor", "40", 40, "ohm"),
        ("rheostat", "4.7k", 4700, "ohm"),
        ("battery", "3.0 U", 3, "V"),
        ("dc_source", "12", 12, "V"),
        ("capacitor", "5", 5e-6, "F"),
        ("inductor", "2", 2, "H"),
    ],
)
def test_bare_values_are_given_with_visible_unit_inference(kind, text, number, unit):
    c = part(kind)
    items = [{"text": text, "bbox": [100, 65, 140, 85], "confidence": 0.9}]
    warnings = associate([c], items)
    assert c.value.number == pytest.approx(number) and c.value.unit == unit
    assert c.value.status == "given" and c.value.source == "ocr"
    assert c.value.unit_inferred and c.value.confidence <= 0.6
    assert ("unit_inferred", c.id) in warnings
    assert items[0]["outcome"] == "assigned" and items[0]["assigned_to"] == c.id


def test_emf_is_source_evidence_not_a_component_name_and_user_values_survive():
    c = part("dc_source", "V1")
    c.value = Value(number=9, unit="V", status="user", source="user", confidence=1)
    items = [{"text": "E = 3.0 V", "bbox": [100, 65, 140, 85], "confidence": 0.99}]
    associate([c], items)
    assert c.label is None and c.value.number == 9 and c.value.source == "user"


@pytest.mark.parametrize("unit", ["অ্যাম্পিয়ার", "অ্যাম্পিয়ার", "ওয়াট", "ওয়াট"])
@pytest.mark.parametrize("form", ["NFC", "NFD"])
def test_bengali_canonical_variants(unit, form):
    result = parse_value(unicodedata.normalize(form, "২ " + unit))
    assert result["number"] == 2 and result["unit"] in {"A", "W"}


def test_word_boxes_group_into_problem_text():
    words = "total current through the resistor in this circuit is unknown".split()
    items = [{"text": word, "bbox": [i * 45, 10, i * 45 + 40, 24]} for i, word in enumerate(words)]
    assert paragraph_text(items) == " ".join(words)


def test_diagonal_wire_cleanup_keeps_adjacent_tiny_text():
    image = np.full((220, 420, 3), 255, np.uint8)
    cv2.line(image, (15, 190), (395, 40), (0, 0, 0), 2)
    cv2.putText(image, "40", (150, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1)
    cleaned, mask = clean_strokes(image)
    assert mask.sum() > 0
    assert np.count_nonzero(cleaned[110:132, 145:180] < 180) > 10


@pytest.mark.parametrize("height", [10, 12, 14])
def test_tiny_touching_label_survives_wire_cleanup_and_gets_anchor(height):
    from circuit_sim.backend.pipeline.ocr_regions import anchored_regions
    from circuit_sim.backend.pipeline.ocr_tiles import candidate_regions

    image = np.full((180, 320, 3), 255, np.uint8)
    scale = height / 22
    cv2.putText(image, "40 Q", (100, 70), cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), 1)
    cv2.line(image, (15, 70), (300, 70), (0, 0, 0), 1)
    cleaned, _ = clean_strokes(image)
    assert np.count_nonzero(cleaned[70 - height : 70, 100:155] < 180) > 10
    _, proposals = anchored_regions(image, [part()], candidate_regions)
    assert any(p.get("component_id") == "R1" for p in proposals)


def test_rotated_crop_uses_both_reading_directions_and_preserves_native_box():
    import time

    class Reader:
        calls = 0

        def recognize(self, image, **kwargs):
            self.calls += 1
            return [([], "40 Ω" if self.calls == 2 else "noise", 0.95)]

    reader = Reader()
    image = np.full((180, 160, 3), 255, np.uint8)
    results = crop_variants(
        image,
        [
            {
                "text": "noise",
                "bbox": [30, 20, 50, 140],
                "component_id": "R1",
                "context": "resistor",
            }
        ],
        reader,
        time.monotonic() + 5,
        {},
    )
    assert any(item["text"] == "40 Ω" and item["rotation"] == -90 for item in results)
    assert all(item["bbox"] == [30, 20, 50, 140] for item in results)


def test_both_engines_run_and_parse_success_wins_over_wrong_confident_text(monkeypatch):
    monkeypatch.setenv("CIRCUIT_OCR_BACKEND", "legacy")
    from circuit_sim.backend.pipeline import text, ocr_tiles, tesseract_regions

    monkeypatch.setattr(text.shutil, "which", lambda name: "local-tesseract")
    monkeypatch.setattr(text, "easy_reader", lambda *a, **k: object())
    calls = []

    def tess(*args, **kwargs):
        calls.append("tesseract")
        return [
            {
                "text": "4 Ω",
                "bbox": [10, 10, 40, 24],
                "confidence": 0.7,
                "engine": "tesseract",
            }
        ]

    def easy(*args, **kwargs):
        calls.append("easyocr")
        return [
            {
                "text": "noise",
                "bbox": [10, 10, 40, 24],
                "confidence": 0.99,
                "engine": "easyocr",
            }
        ]

    monkeypatch.setattr(tesseract_regions, "recognize", tess)
    monkeypatch.setattr(ocr_tiles, "easy_tiles", easy)
    diagnostics = {}
    items, warnings = text.read_text(np.full((100, 100, 3), 255, np.uint8), diagnostics=diagnostics)
    assert calls == ["tesseract", "easyocr"]
    assert items[0]["text"] == "4 Ω"
    assert items[0]["alternatives"][0]["text"] == "noise"
    assert len(diagnostics["engine_readings"]) == 2 and not warnings


def test_failed_engine_is_logged_and_other_engine_survives(monkeypatch, caplog):
    monkeypatch.setenv("CIRCUIT_OCR_BACKEND", "legacy")
    from circuit_sim.backend.pipeline import text, ocr_tiles, tesseract_regions

    monkeypatch.setattr(text.shutil, "which", lambda name: "local-tesseract")
    monkeypatch.setattr(text, "easy_reader", lambda *a, **k: object())
    monkeypatch.setattr(
        tesseract_regions,
        "recognize",
        lambda *a, **k: (_ for _ in ()).throw(RuntimeError("test OCR failure")),
    )
    monkeypatch.setattr(
        ocr_tiles,
        "easy_tiles",
        lambda *a, **k: [{"text": "12 V", "bbox": [10, 10, 40, 24], "confidence": 0.8}],
    )
    diagnostics = {}
    items, warnings = text.read_text(np.full((100, 100, 3), 255, np.uint8), diagnostics=diagnostics)
    assert items[0]["text"] == "12 V" and ("ocr_partial", None) in warnings
    assert diagnostics["stages"][0]["stage"] == "tesseract"
    assert "test OCR failure" in caplog.text


def test_inside_symbol_digit_and_far_arrow_number_are_not_inferred():
    c = part()
    items = [
        {"text": "7", "bbox": [105, 98, 125, 112], "confidence": 0.99},
        {"text": "4", "bbox": [15, 100, 30, 120], "confidence": 0.99},
    ]
    associate([c], items)
    assert c.value.number is None
    assert not any(item.get("assigned_to") for item in items)


def test_digit_from_an_arrow_or_wire_is_not_an_inferred_value():
    c = part()
    items = [
        {
            "text": "1",
            "bbox": [100, 65, 120, 85],
            "confidence": 0.99,
            "wire_overlap": True,
        }
    ]
    associate([c], items)
    assert c.value.number is None and items[0]["reason"] == "weak_context"


def test_conflicting_unitless_readings_require_confirmation():
    c = part()
    items = [
        {
            "text": "332",
            "bbox": [100, 65, 140, 85],
            "confidence": 0.9,
            "alternatives": [{"text": "30", "confidence": 0.6}],
        }
    ]
    associate([c], items)
    assert c.value.number is None and items[0]["reason"] == "weak_context"


def test_crop_endpoint_only_reads_uploaded_crop_and_optin_defaults_off(monkeypatch):
    from fastapi.testclient import TestClient
    from circuit_sim.backend.app.main import app
    from circuit_sim.backend.pipeline import text

    shapes = []

    def read(image, **kwargs):
        shapes.append(image.shape)
        assert not kwargs.get("use_label_reader")
        return [{"text": "3.0 v", "bbox": [0, 0, 40, 18], "confidence": 0.9}], []

    monkeypatch.setattr(text, "read_text", read)
    crop = cv2.imencode(".png", np.full((30, 90, 3), 255, np.uint8))[1].tobytes()
    response = TestClient(app).post(
        "/api/ocr-crop",
        files={"image": ("label.png", crop)},
        data={"component_type": "battery"},
    )
    assert response.status_code == 200
    assert shapes == [(30, 90, 3)]
    assert response.json()["candidates"][0]["parsed"]["number"] == 3


def test_gold_matching_requires_box_overlap_and_does_not_reuse_a_reading(tmp_path):
    import json
    from circuit_sim.backend.tools.ocr_eval import gold_score

    gold = {
        "sha256": "synthetic-test",
        "human_reviewed": True,
        "texts": [
            {"bbox": [10, 10, 40, 20], "text": "4 Ω", "component_id": "R1"},
            {"bbox": [100, 10, 140, 20], "text": "4 Ω", "component_id": "R2"},
        ],
    }
    path = tmp_path / "gold.json"
    path.write_text(json.dumps(gold), encoding="utf-8")
    report = {
        "sha256": "synthetic-test",
        "diagnostics": {"texts": [{"bbox": [10, 10, 40, 20], "text": "4 Ω", "assigned_to": "R1"}]},
    }
    score = gold_score([report], [path])
    assert score["text_accuracy"] == 0.5 and score["assignment_accuracy"] == 0.5
