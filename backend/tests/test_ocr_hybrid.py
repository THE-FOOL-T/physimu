"""Offline hybrid contracts and safety cases, independent of local model binaries."""

import copy
import time
from types import SimpleNamespace
import threading
import unicodedata

import numpy as np
import pytest

from circuit_sim.backend.pipeline.associate import associate
from circuit_sim.backend.pipeline.netlist import Value
from circuit_sim.backend.pipeline.ocr_hybrid.normalize import parse, record, to_native
from circuit_sim.backend.pipeline.ocr_hybrid.rapidocr_adapter import RapidOCRAdapter, output_rows
from circuit_sim.backend.pipeline.ocr_hybrid.bangla_adapter import BanglaAdapter, local_reader
from circuit_sim.backend.pipeline.ocr_hybrid.router import Run, MultiOCRRouter, fuse, read_hybrid
from circuit_sim.backend.pipeline.ocr_hybrid.symbols import PhysicsSymbolCandidateResolver
from circuit_sim.backend.tests.test_associate import make_component, text


def reading(value, x=100, y=60, engine="rapidocr", confidence=0.9, **kwargs):
    box = text(value, x, y)["bbox"]
    a, b, c, d = box
    return record(value, [[a, b], [c, b], [c, d], [a, d]], confidence, engine, **kwargs)


def run():
    return Run(time.monotonic() + 20, lambda: None, {})


@pytest.mark.parametrize(
    "raw,number,unit",
    [
        ("R3 = 4.7 kΩ", 4700, "ohm"),
        ("১০ ওহম", 10, "ohm"),
        ("১২ ভোল্ট", 12, "V"),
        ("100 µF", 100e-6, "F"),
        ("20 mH", 0.02, "H"),
        ("R₁=10 Ω", 10, "ohm"),
        ("1MΩ", 1e6, "ohm"),
        ("3.0 v", 3, "V"),
    ],
)
def test_strict_si(raw, number, unit):
    value = parse(raw)
    assert value["number"] == pytest.approx(number)
    assert value["unit"] == unit and not value["unit_inferred"]


@pytest.mark.parametrize("raw", ["V=6V", "V = 6 V", "V = 6000 mV", "V=৬ V"])
def test_bare_voltage_equation_is_explicit_source_value_without_printed_identity(raw):
    value = parse(raw, "dc_source")
    assert value["number"] == pytest.approx(6)
    assert value["unit"] == "V" and value["label"] is None
    assert not value["unit_inferred"]
    assert parse(raw, "resistor") is None
    assert parse(raw, "voltmeter") is None
    assert parse(raw)["number"] == pytest.approx(6)


@pytest.mark.parametrize("raw", ["V=6", "V=6 ohm", "V(R1)=6 V", "voltage V=6 V", "V=?"])
def test_generic_voltage_cannot_supply_a_missing_unit_or_parse_measurement_prose(raw):
    assert parse(raw) is None


def test_low_quality_alternative_does_not_veto_clear_source_reading():
    result = fuse(
        [reading("V=6V", confidence=0.99985), reading("161", engine="easyocr-bn", confidence=0.047)]
    )
    assert not result[0]["ocr_conflict"]
    assert result[0]["alternatives"][0]["text"] == "161"
    source = make_component("V1", "dc_source", 100)
    associate([source], result)
    assert source.value.number == 6 and source.value.source == "ocr"


@pytest.mark.parametrize("raw", ["10", "8", "R1=12", "100", "5"])
def test_no_digit_to_symbol_or_common_value_prior(raw):
    v = parse(raw, "capacitor")
    assert v["unit"] is None
    assert v["number"] == float(raw.split("=")[-1])


@pytest.mark.parametrize(
    "raw",
    [
        "current through R1 is 2 A",
        "V(R1) = 12 V",
        "voltage between A and B = 12 V",
        "R1 = 1O Ω",
        "10 Q",
    ],
)
def test_measurements_and_unconfirmed_symbols_are_not_component_values(raw):
    assert parse(raw) is None


def test_symbols_are_evidence_only():
    r = PhysicsSymbolCandidateResolver()
    original = reading("10 Q")
    item = r.enrich(copy.deepcopy(original))
    assert item["text"] == original["text"] and item["raw_text"] == "10 Q"
    assert item["symbol_proposals"][0]["text"] == "10 Ω"
    assert "symbol_proposals" not in r.enrich(reading("10"))
    assert "symbol_proposals" not in r.enrich(reading("8"))


@pytest.mark.parametrize(
    "rotation,points",
    [
        (0, [[2, 3], [12, 8]]),
        (90, [[17, 2], [12, 12]]),
        (180, [[28, 17], [18, 12]]),
        (270, [[3, 28], [8, 18]]),
    ],
)
def test_native_coordinate_inverse_all_quarter_turns(rotation, points):
    assert to_native(points, 30, 20, rotation, (100, 200)) == [[102, 203], [112, 208]]


def test_provider_output_normalization():
    polygon = [[1, 2], [12, 2], [12, 8], [1, 8]]
    rows = [(polygon, "6 Ω", 0.92)]
    assert output_rows((rows, [])) == rows
    assert output_rows(SimpleNamespace(boxes=[polygon], txts=["6 Ω"], scores=[0.92])) == rows
    assert output_rows(SimpleNamespace(boxes=None, txts=None, scores=None)) == []
    item = record("6 Ω", polygon, 0.92, "rapidocr", rotation=180)
    assert item["bbox"] == [1, 2, 12, 8] and item["confidence"] == 0.92


@pytest.mark.parametrize("vertical", [False, True])
def test_rapid_classification_retry_keeps_exact_box_and_real_angle(vertical):
    polygon = [
        [20, 10],
        [30 if vertical else 80, 10],
        [30 if vertical else 80, 90 if vertical else 30],
        [20, 90 if vertical else 30],
    ]
    calls = []

    class Engine:
        def __call__(self, image, **flags):
            calls.append(flags)
            if flags["use_det"]:
                return SimpleNamespace(boxes=[polygon])
            if flags["use_cls"]:
                return SimpleNamespace(cls_res=[("0", 0.99)])
            count = sum(c["use_rec"] for c in calls)
            return SimpleNamespace(
                txts=["U9=" if count == 1 else "6 Ω"], scores=[0.73 if count == 1 else 0.92]
            )

    result = RapidOCRAdapter(engine=Engine()).extract(np.full((120, 120, 3), 255, np.uint8), run())
    assert len(result) == 2 and result[1]["text"] == "6 Ω"
    assert result[1]["rotation"] == (270 if vertical else 180)
    assert result[1]["bbox"] == [20, 10, 30 if vertical else 80, 90 if vertical else 30]
    assert len(calls) == 4


def test_classifier_flip_is_recorded_and_valid_labels_are_not_retried():
    class Engine:
        def __call__(self, image, **flags):
            if flags["use_det"]:
                return SimpleNamespace(boxes=[[[10, 10], [80, 10], [80, 30], [10, 30]]])
            if flags["use_cls"]:
                return SimpleNamespace(cls_res=[("180", np.float32(0.99))])
            return SimpleNamespace(txts=["6 Ω"], scores=[0.92])

    result = RapidOCRAdapter(engine=Engine()).extract(np.zeros((100, 100, 3), np.uint8), run())
    assert len(result) == 1 and result[0]["rotation"] == 180
    import json

    json.dumps(result)


def test_bengali_nfc_preserves_original_and_native_coordinates():
    raw = unicodedata.normalize("NFD", "২ অ্যাম্পিয়ার")

    class Reader:
        def recognize(self, image, **kwargs):
            assert kwargs["workers"] == 0
            return [([[10, 20], [60, 20], [60, 40], [10, 40]], raw, 0.87)]

    output = BanglaAdapter(reader=Reader()).extract(np.zeros((100, 100, 3), np.uint8), run())
    assert output[0]["raw_text"] == raw
    assert unicodedata.is_normalized("NFC", output[0]["normalized_text"])
    assert parse(output[0]["text"])["number"] == 2
    assert output[0]["bbox"] == [10, 20, 60, 40]


def test_bengali_uses_independent_small_proposals_and_preserves_native_offsets():
    import cv2

    image = np.full((700, 1100, 3), 255, np.uint8)
    cv2.putText(image, "12 V", (750, 420), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    component = SimpleNamespace(bbox=(600, 350, 620, 450))
    shapes = []

    class Reader:
        def recognize(self, crop, **kwargs):
            h, w = crop.shape[:2]
            shapes.append((h, w))
            return [([[0, 0], [w, 0], [w, h], [0, h]], "১২ ভোল্ট", 0.9)]

    output = BanglaAdapter(reader=Reader()).extract(image, run(), [component])
    assert output and shapes
    assert all(h < 100 and w < 300 for h, w in shapes)
    assert all(700 < row["bbox"][0] < row["bbox"][2] < 950 for row in output)
    assert all(350 < row["bbox"][1] < row["bbox"][3] < 450 for row in output)
    assert all(parse(row["text"])["number"] == 12 for row in output)


def test_micro_aliases_normalize_only_in_numeric_unit_position():
    from circuit_sim.backend.pipeline.ocr_hybrid.normalize import normalize

    assert {normalize(s).replace(" ", "") for s in ("100 uF", "100 µF", "100 μF")} == {"100µF"}
    assert normalize("u = unknown") == "u = unknown"


def test_bangla_singleton_disables_downloads(monkeypatch, tmp_path):
    import sys
    from circuit_sim.backend import inference

    calls = []
    monkeypatch.setattr(inference, "configure_threads", lambda: None)
    monkeypatch.setattr(
        "circuit_sim.backend.pipeline.ocr_hybrid.bangla_adapter.configure_threads", lambda: None
    )
    monkeypatch.setitem(
        sys.modules,
        "easyocr",
        SimpleNamespace(Reader=lambda *a, **k: calls.append((a, k)) or object()),
    )
    local_reader.cache_clear()
    try:
        assert local_reader(str(tmp_path)) is local_reader(str(tmp_path))
        assert len(calls) == 1 and calls[0][1]["download_enabled"] is False
        assert calls[0][1]["detector"] is False
        assert calls[0][0] == (["bn", "en"],)
    finally:
        local_reader.cache_clear()


def test_semantic_reading_beats_invalid_high_confidence_without_losing_provenance():
    items = [
        reading("noise", engine="easyocr-bn", confidence=0.99),
        reading("10 Ω", confidence=0.7),
    ]
    result = fuse(items)
    assert len(result) == 1 and result[0]["text"] == "10 Ω"
    assert result[0]["alternatives"][0]["text"] == "noise"
    assert set(result[0]["provenance"]) == {"easyocr-bn", "rapidocr"}
    assert items[0].get("alternatives") is None


def test_raw_scores_do_not_rank_different_engines():
    result = fuse(
        [reading("10 Ω", confidence=0.7), reading("10 Ω", engine="easyocr-bn", confidence=0.99)]
    )
    assert result[0]["engine"] == "rapidocr" and not result[0]["ocr_conflict"]


def test_adjacent_overlapping_and_nested_different_labels_are_not_merged():
    a, b = reading("R1"), reading("R2", x=108)
    assert len(fuse([a, b])) == 2
    a, b = reading("10 Ω"), reading("20 Ω", x=115)
    assert len(fuse([a, b])) == 2
    a, b = reading("R1 = 10 Ω"), reading("R2")
    b["bbox"] = [95, 57, 105, 63]
    assert len(fuse([a, b])) == 2


@pytest.mark.parametrize("other", ["100", "100 Ω", "10 V"])
def test_disagreements_require_review_even_for_explicit_primary(other):
    item = fuse([reading("10 Ω"), reading(other, engine="easyocr-bn")])[0]
    c = make_component("R1", "resistor", 100)
    associate([c], [item])
    assert c.value.number is None and item["reason"] == "ocr_conflict"
    assert item["alternatives"][0]["text"] == other


def test_close_resistors_and_combined_si():
    cs = [make_component("x", "resistor", 100), make_component("y", "resistor", 180)]
    items = [reading("R1 = 10 Ω"), reading("R2 = 20 Ω", x=180)]
    associate(cs, items)
    assert [(c.label, c.value.number) for c in cs] == [("R1", 10), ("R2", 20)]
    assert all(len({a["component_id"] for a in i["assignments"]}) == 1 for i in items)
    c = make_component("x", "resistor", 100)
    item = reading("R3 = 4.7 kΩ")
    associate([c], [item])
    assert (c.label, c.value.number) == ("R3", 4700)
    assert item["raw"] == item["text"] == "R3 = 4.7 kΩ"


def test_separate_identity_value_and_known_identity_protection():
    cs = [make_component("a", "resistor", 100), make_component("b", "resistor", 180)]
    items = [
        reading("R1", y=55),
        reading("10 Ω", y=40),
        reading("R2", x=180, y=55),
        reading("20 Ω", x=180, y=40),
    ]
    associate(cs, items)
    assert [(c.label, c.value.number) for c in cs] == [("R1", 10), ("R2", 20)]
    cs[0].value = Value()
    item = reading("R2 = 5 Ω")
    associate(cs, [item])
    assert cs[0].label == "R1" and cs[0].value.number is None
    assert any(c["reason"] == "identity_conflict" for c in item["candidates"])


def test_wrong_unit_bengali_and_ambiguous_midpoint():
    cs = [make_component("R1", "resistor", 100), make_component("V1", "dc_source", 160)]
    items = [reading("১২ ভোল্ট", x=155), reading("১০ ওহম")]
    associate(cs, items)
    assert [c.value.number for c in cs] == [10, 12]
    cs = [make_component("R1", "resistor", 100), make_component("R2", "resistor", 160)]
    item = reading("10 Ω", x=130)
    associate(cs, [item])
    assert all(c.value.number is None for c in cs) and item["reason"] == "ambiguous"


@pytest.mark.parametrize("raw", ["10", "R1 = 12", "7", "10 Q"])
def test_unsupported_wire_or_body_readings_never_become_values(raw):
    c = make_component("R1", "resistor", 100)
    item = reading(raw, y=100, wire_overlap=True)
    associate([c], [item])
    assert c.value.number is None


def test_user_value_and_confirmed_region_survive_repeated_assignment():
    c = make_component("R1", "resistor", 100)
    c.value = Value(number=220, unit="ohm", status="user", source="user", confidence=1)
    item = reading("10 Ω")
    for _ in range(2):
        associate([c], [item])
        assert c.value.number == 220 and item["reason"] == "user_value_protected"
        assert not item.get("association")
    item.update(user_confirmed=True, outcome="ignored", reason="ignored")
    associate([c], [item])
    assert item["outcome"] == "ignored" and item["reason"] == "ignored"


class FakeEngine:
    def __init__(self, name, output=None, error=None):
        self.name, self.output, self.error = name, output or [], error
        self.calls = 0

    def extract(self, image, run, components=None):
        run.available()
        self.calls += 1
        if self.error:
            raise self.error
        return self.output


def test_partial_failure_budget_cancellation_and_missing_models():
    image = np.full((150, 250, 3), 255, np.uint8)
    diagnostics = {}
    router = MultiOCRRouter(
        primary=FakeEngine("rapidocr", error=ImportError("onnxruntime missing")),
        bangla=FakeEngine("easyocr-bn", [reading("১০ ওহম", engine="easyocr-bn")]),
    )
    items, warnings = router.extract(
        image, diagnostics=diagnostics, deadline=time.monotonic() + 10, check=lambda: None
    )
    assert len(items) == 1 and ("ocr_partial", None) in warnings
    assert diagnostics["stages"][0]["error_type"] == "ImportError"
    assert diagnostics["engine_readings"][0]["raw_text"] == "১০ ওহম"
    items, warnings = router.extract(image, diagnostics={}, deadline=0, check=lambda: None)
    assert items == [] and ("time_budget", None) in warnings
    from circuit_sim.backend.app.jobs import Cancelled

    with pytest.raises(Cancelled):
        router.extract(
            image,
            diagnostics={},
            deadline=time.monotonic() + 10,
            check=lambda: (_ for _ in ()).throw(Cancelled()),
        )
    with pytest.raises(FileNotFoundError, match="local detector"):
        RapidOCRAdapter().get_engine()


def test_deadline_does_not_load_models_and_lock_is_released_on_cancel(monkeypatch):
    from circuit_sim.backend.app.jobs import Cancelled

    lock = threading.Lock()
    image = np.zeros((10, 10, 3), np.uint8)
    assert read_hybrid(image, None, {}, 0, lambda: None, lock, {})[0] == []
    assert not lock.locked()

    def fail(*args, **kwargs):
        raise Cancelled()

    monkeypatch.setattr(MultiOCRRouter, "extract", fail)
    with pytest.raises(Cancelled):
        read_hybrid(image, None, {}, time.monotonic() + 10, lambda: None, lock, {})
    assert not lock.locked()


def test_two_failed_engines_return_diagnostics_without_breaking_the_request():
    router = MultiOCRRouter(
        primary=FakeEngine("rapidocr", error=ImportError("onnxruntime missing")),
        bangla=FakeEngine(
            "easyocr-bn", error=FileNotFoundError("bengali.pth missing; downloads disabled")
        ),
    )
    diagnostics = {}
    items, warnings = router.extract(
        np.zeros((30, 40, 3), np.uint8),
        diagnostics=diagnostics,
        deadline=time.monotonic() + 10,
        check=lambda: None,
    )
    assert items == [] and ("ocr_unavailable", None) in warnings
    assert ("ocr_failed", None) in warnings
    assert len(diagnostics["stages"]) == 2


@pytest.mark.parametrize("dotted", [False, True])
def test_hybrid_unassigned_boxes_do_not_change_crossing_topology(dotted):
    from circuit_sim.backend.tests.test_wires import cross
    from circuit_sim.backend.pipeline.wires import trace

    image, cs = cross(dotted)
    original = copy.deepcopy(cs)
    trace(image, original)
    item = reading("10 Ω", x=100, y=100, confidence=0.4)
    router = MultiOCRRouter(primary=FakeEngine("rapidocr", [item]), bangla=FakeEngine("easyocr-bn"))
    items, _ = router.extract(
        image, components=cs, diagnostics={}, deadline=time.monotonic() + 10, check=lambda: None
    )
    associate(cs, items)
    assert items[0]["wire_overlap"] and items[0]["outcome"] != "assigned"
    trace(image, cs, items)
    assert [t.node for c in cs for t in c.terminals] == [
        t.node for c in original for t in c.terminals
    ]


@pytest.mark.parametrize("dotted", [False, True])
def test_even_assigned_hybrid_text_must_not_erase_a_crossing(dotted):
    from circuit_sim.backend.tests.test_wires import cross
    from circuit_sim.backend.pipeline.wires import trace

    image, cs = cross(dotted)
    original = copy.deepcopy(cs)
    trace(image, original)
    router = MultiOCRRouter(
        primary=FakeEngine("rapidocr", [reading("10 Ω", x=100, y=100)]),
        bangla=FakeEngine("easyocr-bn"),
    )
    items, _ = router.extract(
        image, diagnostics={}, deadline=time.monotonic() + 10, check=lambda: None
    )
    # Assignment is not permission to erase electrical junction ink.
    items[0].update(outcome="assigned", assigned_to=cs[0].id)
    trace(image, cs, items)
    assert [t.node for c in cs for t in c.terminals] == [
        t.node for c in original for t in c.terminals
    ]


def test_feature_flag_preserves_legacy_and_external_reader_optin(monkeypatch):
    from circuit_sim.backend.pipeline import text as public, ocr_tiles

    monkeypatch.setenv("CIRCUIT_OCR_BACKEND", "legacy")
    monkeypatch.setattr(public.shutil, "which", lambda name: None)
    monkeypatch.setattr(public, "easy_reader", lambda *a: object())
    monkeypatch.setattr(ocr_tiles, "easy_tiles", lambda *a, **k: [reading("legacy")])
    assert public.read_text(np.zeros((100, 100, 3), np.uint8))[0][0]["text"] == "legacy"

    def hybrid(*args, **kwargs):
        return [reading("10 Ω", confidence=0.6)], []

    monkeypatch.setattr("circuit_sim.backend.pipeline.ocr_hybrid.router.read_hybrid", hybrid)

    class Remote:
        calls = 0

        def read_labels(self, image):
            self.calls += 1
            return []

    remote = Remote()
    monkeypatch.setattr(public, "_vlm", remote)
    monkeypatch.setenv("CIRCUIT_OCR_BACKEND", "hybrid")
    public.read_text(np.zeros((100, 100, 3), np.uint8))
    assert remote.calls == 0
    public.read_text(np.zeros((100, 100, 3), np.uint8), use_label_reader=True)
    assert remote.calls == 1


def test_rapid_explicit_paths_and_character_preflight_never_need_downloads(monkeypatch, tmp_path):
    import sys
    from enum import Enum
    from circuit_sim.backend.pipeline.ocr_hybrid.rapidocr_adapter import local_engine

    paths = [tmp_path / name for name in ("det.onnx", "rec.onnx", "cls.onnx")]
    for path in paths:
        path.write_bytes(b"test")
    params = []

    class EngineType(Enum):
        ONNXRUNTIME = "onnxruntime"

    session = SimpleNamespace(
        get_modelmeta=lambda: SimpleNamespace(custom_metadata_map={"character": "0\n1\nΩ"})
    )
    monkeypatch.setitem(
        sys.modules,
        "onnxruntime",
        SimpleNamespace(
            SessionOptions=lambda: SimpleNamespace(), InferenceSession=lambda *a, **k: session
        ),
    )
    monkeypatch.setitem(
        sys.modules,
        "rapidocr",
        SimpleNamespace(
            RapidOCR=lambda **k: params.append(k["params"]) or object(), EngineType=EngineType
        ),
    )
    local_engine.cache_clear()
    try:
        adapter = RapidOCRAdapter(
            dict(zip(("detector", "recognizer", "classifier"), map(str, paths)))
        )
        assert adapter.get_engine() is adapter.get_engine()
        assert params[0]["Rec.model_path"] == str(paths[1])
        assert all(
            params[0][part + ".engine_type"] is EngineType.ONNXRUNTIME
            for part in ("Det", "Rec", "Cls")
        )
        local_engine.cache_clear()
        session.get_modelmeta = lambda: SimpleNamespace(custom_metadata_map={})
        with pytest.raises(ValueError, match="embedded characters"):
            adapter.get_engine()
        assert len(params) == 1
    finally:
        local_engine.cache_clear()


def test_hybrid_analysis_and_crop_api_keep_envelope_and_topology(monkeypatch):
    import cv2
    from fastapi.testclient import TestClient
    from circuit_sim.backend.app.main import app
    from circuit_sim.backend.pipeline.engine import analyze_image
    from circuit_sim.backend.tests.test_wire_round3 import diagram

    image, cs, marks = diagram()
    # Exact synthetic detections isolate OCR/association from detector accuracy.
    for c in cs:
        c.value = Value(unit="ohm" if c.type == "resistor" else "V")
    boxes = [
        record("100 Ω", [[100, 20], [140, 20], [140, 35], [100, 35]], 0.9, "rapidocr"),
        record("3 V", [[195, 210], [225, 210], [225, 225], [195, 225]], 0.9, "rapidocr"),
    ]

    def extract(*args, **kwargs):
        return copy.deepcopy(boxes), []

    monkeypatch.setenv("CIRCUIT_OCR_BACKEND", "hybrid")
    monkeypatch.setattr("circuit_sim.backend.pipeline.ocr_hybrid.router.read_hybrid", extract)
    output = analyze_image(image, detections=(cs, marks))
    assert output["netlist"]["version"] == 1 and len(output["netlist"]["nodes"]) == 2
    assert abs(output["solution"]["components"]["R1"]["current"]) == pytest.approx(0.03)
    assert output["diagnostics"]["texts"][0]["raw_text"] == "100 Ω"
    assert {"timings", "warnings", "regions", "provenance", "source_image"} <= output.keys()
    data = cv2.imencode(".png", np.full((30, 90, 3), 255, np.uint8))[1].tobytes()
    response = TestClient(app).post("/api/ocr-crop", files={"image": ("label.png", data)})
    assert response.status_code == 200
    assert {"candidates", "warnings", "diagnostics"} <= response.json().keys()
    assert response.json()["candidates"][0]["engine"] == "rapidocr"


def test_hybrid_crop_api_uses_same_strict_parser_as_association(monkeypatch):
    import cv2
    from fastapi.testclient import TestClient
    from circuit_sim.backend.app.main import app

    monkeypatch.setenv("CIRCUIT_OCR_BACKEND", "hybrid")
    monkeypatch.setattr(
        "circuit_sim.backend.pipeline.ocr_hybrid.router.read_hybrid",
        lambda *a, **k: ([reading("R1 = 12")], []),
    )
    data = cv2.imencode(".png", np.full((30, 90, 3), 255, np.uint8))[1].tobytes()
    result = TestClient(app).post("/api/ocr-crop", files={"image": ("label.png", data)}).json()
    value = result["candidates"][0]["parsed"]
    assert value["number"] == 12 and value["unit"] is None


def test_hybrid_still_solves_the_global_collision():
    cs = [make_component("a", "resistor", 100), make_component("b", "resistor", 200)]
    items = [
        reading("10 Ω", x=140, y=70),
        reading("4 Ω", y=70),
        reading("R1", y=50),
        reading("R2", x=200, y=50),
    ]
    associate(cs, items)
    assert [(c.label, c.value.number) for c in cs] == [("R1", 4), ("R2", 10)]


def test_established_identity_cannot_be_duplicated_on_another_component():
    cs = [make_component("a", "resistor", 100), make_component("b", "resistor", 200)]
    cs[0].label = "R1"
    item = reading("R1 = 10 Ω", x=200)
    associate(cs, [item])
    assert cs[1].label is None and cs[1].value.number is None
    assert any(
        c["component_id"] == "b" and c["reason"] == "identity_conflict" for c in item["candidates"]
    )


def test_evaluation_keeps_coverage_precision_and_ambiguity_separate():
    from circuit_sim.backend.tools.hybrid_ocr_eval import metrics

    a, b = reading("10 Ω"), reading("20 Ω", x=200)
    a["assigned_to"], b["assigned_to"] = "R2", "R1"
    gold = [dict(a, component_id="R1"), dict(b, component_id="R2")]
    result = metrics([a, b], gold)
    assert result["association_coverage"] == 1 and result["association_precision"] == 0
    assert (
        result["false_assignments"] == 2 and result["correct_component_value_assignment_rate"] == 0
    )
    assert (
        metrics([], [dict(a, component_id=None, ambiguous=True)])["ambiguous_correctly_unassigned"]
        == 0
    )


def test_evaluation_does_not_miscount_a_correct_name_subspan_as_a_false_assignment():
    from circuit_sim.backend.tools.hybrid_ocr_eval import metrics

    name = reading("R1")
    name["assigned_to"] = "R1"
    gold = [{"text": "R1 = 10 Ω", "bbox": [80, 50, 180, 70], "component_id": "R1"}]
    result = metrics([name], gold)
    assert result["false_assignments"] == 0 and result["association_precision"] == 1
    assert result["correct_component_value_assignment_rate"] == 0
