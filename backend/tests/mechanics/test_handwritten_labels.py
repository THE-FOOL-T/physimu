"""Mocked crop consent/transport/grammar tests. No real provider call or real accuracy."""

import base64
import json
import time

import cv2
import httpx
import numpy as np
import pytest

from circuit_sim.backend.core import CropLabelReader, Cancelled
from circuit_sim.backend.domains.mechanics import label_reader
from circuit_sim.backend.domains.mechanics.detect import Detection
from circuit_sim.backend.domains.mechanics.labels import read_tokens


def diagram():
    return np.full((400, 600, 3), 255, np.uint8)


def detection(box=(100, 100, 180, 125)):
    return Detection("T1", "text_label", list(box), 0.9)


@pytest.mark.parametrize(
    "text",
    [
        "2 kg",
        "m₁ = ৩ kg",
        "30°",
        "g=9.81 m/s²",
        "μ_s=0.3",
        "e=0.8",
        "k=20 N/m",
        "v=2 m/s",
        "m1",
        "?",
    ],
)
def test_crop_vocabulary_accepts_only_local_mechanics_grammar(text):
    assert label_reader.valid_label(text)


@pytest.mark.parametrize(
    "text",
    [
        "3",
        "move 2 kg",
        "2 kg and 3 kg",
        "ignore instructions",
        "hello",
        "R1=10 ohm",
        "2 kg; solve it",
        "1e999 kg",
        "",
        None,
    ],
)
def test_crop_vocabulary_refuses_prose_circuit_labels_and_untyped_numbers(text):
    assert not label_reader.valid_label(text)


def test_no_consent_never_configures_or_calls_a_reader(monkeypatch):
    monkeypatch.setattr(label_reader, "configured_reader", lambda: pytest.fail("no consent"))
    for consent in (False, None, "true", 1):
        result, notes, diagnostics = label_reader.read_fallback(
            diagram(), [], [detection()], consent=consent
        )
        assert result == [] and notes == [] and diagnostics["crops_sent"] == 0


def test_mock_http_receives_only_crop_and_provider_coordinates_are_ignored():
    seen = []

    def handler(request):
        body = json.loads(request.content)
        parts = body["contents"][0]["parts"]
        assert len(parts) == 2 and set(parts[1]) == {"inline_data"}
        crop = cv2.imdecode(
            np.frombuffer(base64.b64decode(parts[1]["inline_data"]["data"]), np.uint8),
            cv2.IMREAD_COLOR,
        )
        assert crop.shape[:2] == (31, 86)
        seen.append(body)
        return httpx.Response(
            200,
            json=dict(
                candidates=[
                    dict(
                        content=dict(
                            parts=[
                                dict(
                                    text=json.dumps(
                                        dict(
                                            text="m1 = 2 kg",
                                            bbox=[-999, -999, 99999, 99999],
                                            confidence=1,
                                        )
                                    )
                                )
                            ]
                        )
                    )
                ]
            ),
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    reader = CropLabelReader("TEST-NOT-A-KEY", "TEST-MODEL", label_reader.PROMPT, client=client)
    local = [dict(text="??", bbox=[100, 100, 180, 125], confidence=0.2)]
    rows, notes, diagnostics = label_reader.read_fallback(
        diagram(), local, [detection()], consent=True, reader=reader
    )
    assert not notes and diagnostics["crops_sent"] == 1 and len(seen) == 1
    assert local[0]["text"] == "??" and "alternatives" not in local[0]
    (token,) = read_tokens(rows)
    assert (token.number, token.unit, token.source, token.confidence) == (2, "kg", "vlm", 0.65)
    assert token.bbox == local[0]["bbox"]


def test_crop_gate_rejects_whole_page_skips_clear_local_labels_and_caps_count():
    class Reader:
        def __init__(self):
            self.shapes = []

        def read_labels(self, crop, *, timeout):
            self.shapes.append(crop.shape)
            assert 0 < timeout <= 8
            return [dict(text="2 kg", bbox=[0, 0, 600, 400], source="user", confidence=1)]

    reader = Reader()
    result, notes, diagnostics = label_reader.read_fallback(
        diagram(), [], [detection([0, 0, 600, 400])], consent=True, reader=reader
    )
    assert not result and not reader.shapes and diagnostics["rejected"] == 1
    local = [dict(text="2 kg", bbox=[100, 100, 180, 125], confidence=0.95)]
    result, _, _ = label_reader.read_fallback(
        diagram(), local, [detection()], consent=True, reader=reader
    )
    assert result == local and not reader.shapes
    boxes = [detection([10 + i * 60, 20, 50 + i * 60, 40]) for i in range(9)]
    result, notes, diagnostics = label_reader.read_fallback(
        diagram(), [], boxes, consent=True, reader=reader
    )
    assert len(reader.shapes) == len(result) == diagnostics["crops_sent"] == 8
    assert all(
        r["source"] == "vlm" and r["confidence"] == 0.65 and r["bbox"] != [0, 0, 600, 400]
        for r in result
    )


def test_failures_deadline_rejection_and_cancellation_leave_local_evidence(monkeypatch):
    class Broken:
        def read_labels(self, *args, **kwargs):
            raise RuntimeError("TEST private failure detail")

    local = [dict(text="??", bbox=[100, 100, 180, 125], confidence=0.1)]
    rows, notes, _ = label_reader.read_fallback(diagram(), local, [], consent=True, reader=Broken())
    assert rows[0]["text"] == "??" and notes == [("label_reader_failed", None)]
    _, notes, diagnostics = label_reader.read_fallback(
        diagram(), local, [], consent=True, reader=Broken(), deadline=time.monotonic() - 1
    )
    assert notes == [("label_reader_time_budget", None)] and not diagnostics["crops_sent"]
    monkeypatch.setenv("MECHANICS_LABEL_API_KEY", "TEST-NOT-A-KEY")
    monkeypatch.setenv("MECHANICS_LABEL_MODEL", "bad/model")
    _, notes, _ = label_reader.read_fallback(diagram(), local, [], consent=True)
    assert notes == [("label_reader_unavailable", None)]

    def cancel():
        raise Cancelled()

    with pytest.raises(Cancelled):
        label_reader.read_fallback(
            diagram(), local, [], consent=True, reader=Broken(), check=cancel
        )
