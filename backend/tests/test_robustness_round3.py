import json
import gc
import weakref
import threading
import time
from pathlib import Path

import numpy as np
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from circuit_sim.backend.app.jobs import JobStore, Cancelled
from circuit_sim.backend.app.limits import RateLimiter
from circuit_sim.backend.app.main import app
from circuit_sim.backend.inference import thread_count
from circuit_sim.backend.pipeline.budget import Budget, BudgetExpired
from circuit_sim.backend.pipeline.netlist import Meta, Netlist
from circuit_sim.backend.pipeline.warnings import ordered
from circuit_sim.backend.pipeline import engine, text

ROOT = Path(__file__).resolve().parents[2]


def test_cancelled_queued_runner_releases_its_image_payload():
    store = JobStore(limit=1)
    gate, entered = threading.Event(), threading.Event()

    def block(progress):
        entered.set()
        gate.wait(3)

    class Payload:
        pass

    def make_runner():
        payload = Payload()
        return lambda progress: payload, weakref.ref(payload)

    try:
        first = store.start(block)
        assert entered.wait(1)
        store.cancel(first)
        runner, reference = make_runner()
        queued = store.start(runner)
        del runner
        assert reference() is not None
        store.cancel(queued)
        gc.collect()
        assert reference() is None
    finally:
        gate.set()
        store.executor.shutdown(wait=True)


def test_three_cancels_release_slots_even_while_a_native_call_is_blocked():
    store = JobStore(limit=1)
    entered, gate = threading.Event(), threading.Event()

    def blocked(progress):
        entered.set()
        gate.wait(3)
        progress("text")
        return {"ok": True}

    try:
        first = store.start(blocked)
        assert entered.wait(1)
        store.cancel(first)
        assert store.active == 0
        for _ in range(3):
            queued = store.start(blocked)
            assert store.get(queued)["stage"] == "queued"
            store.cancel(queued)
            assert store.active == 0
        last = store.start(lambda progress: {"ok": True})
        gate.set()
        for _ in range(100):
            if store.get(last)["result"]:
                break
            time.sleep(0.005)
        assert store.get(last)["result"] == {"ok": True}
        assert store.get(first)["result"] is None
        assert store.active == 0
    finally:
        gate.set()
        store.executor.shutdown(wait=True)


def test_server_error_logs_type_and_request_id(caplog):
    store = JobStore(limit=1)

    def fail(progress):
        raise RuntimeError("model unavailable")

    try:
        id_ = store.start(fail, request_id="request-example")
        for _ in range(100):
            if store.get(id_)["error"]:
                break
            time.sleep(0.005)
        assert store.get(id_)["error"]["message_key"] == "error.server_error"
        assert "request-example" in caplog.text and "RuntimeError" in caplog.text
    finally:
        store.executor.shutdown(wait=True)


def test_expired_page_keeps_all_detected_parts_without_retry(monkeypatch):
    net = Netlist.model_validate(
        json.loads((ROOT / "fixtures/editor_loop.json").read_text())["netlist"]
    )
    monkeypatch.setattr(text, "read_text", lambda *a, **k: ([], []))
    monkeypatch.setattr(
        engine, "prepare_trace", lambda *a, **k: pytest.fail("expired trace started")
    )
    result = engine.analyze_image(
        np.full((400, 600, 3), 255, np.uint8),
        detections=(net.components, []),
        budget=Budget(seconds=0),
    )
    parsed = Netlist.model_validate(result["netlist"])
    assert len(parsed.components) == len(net.components)
    assert parsed.meta.provenance == "partial"
    assert any(w.code == "time_budget" for w in parsed.warnings)


def test_page_and_stage_deadlines_are_bounded():
    clock = [0]
    budget = Budget(seconds=25, clock=lambda: clock[0])
    assert budget.deadline("text") <= 25
    clock[0] = 26
    with pytest.raises(BudgetExpired):
        budget.check("wires")
    assert "wires" in budget.exceeded


def test_ocr_deadline_preserves_downstream_time_even_late_in_page():
    clock = [0]
    budget = Budget(seconds=25, clock=lambda: clock[0])
    clock[0] = 7
    text_end = budget.deadline("text", reserve=10)
    clock[0] = text_end
    assert budget.available("wires")
    assert budget.end - clock[0] >= 10


@pytest.mark.parametrize("endpoint", ["solve", "resolve"])
def test_api_never_echoes_embedded_image(endpoint):
    net = json.loads((ROOT / "fixtures/series.json").read_text())["netlist"]
    net["image"]["path"] = "data:image/png;base64," + "A" * 1_000_000
    response = TestClient(app).post("/api/" + endpoint, json={"netlist": net})
    assert response.status_code == 200
    assert response.json()["netlist"]["image"]["path"] == ""
    assert len(response.content) < 20_000


def test_request_size_and_validation_errors_are_typed():
    client = TestClient(app)
    too_big = client.post("/api/solve", content=b"x" * (22 * 1024 * 1024))
    assert too_big.status_code == 413
    assert too_big.json()["detail"] == {"code": "too_large", "message_key": "error.too_large"}
    invalid = client.post("/api/solve", json={"netlist": {}})
    # Empty is a valid v1 netlist, so exercise a forbidden version explicitly.
    invalid = client.post("/api/solve", json={"netlist": {"version": 2}})
    assert invalid.status_code == 422
    assert invalid.json()["detail"]["message_key"] == "error.invalid_request"


def test_rate_limit_expires_and_does_not_mix_clients():
    now = [0]
    limiter = RateLimiter(limit=2, seconds=60, clock=lambda: now[0])
    assert limiter.allow("a") and limiter.allow("a")
    assert not limiter.allow("a") and limiter.allow("b")
    now[0] = 61
    assert limiter.allow("a")
    assert "b" not in limiter.clients


def test_provenance_aliases_and_stable_warning_priority():
    for alias in ["automatic", "saved", "example", "synthetic exact geometry"]:
        assert Meta(provenance=alias).provenance == "extracted"
    with pytest.raises(ValidationError):
        Meta(provenance="invented")
    warnings = [
        {"code": code, "ref": ref, "message_key": "warn." + code}
        for code, ref in [
            ("assumed_value", "R2"),
            ("source_open_loop", "V1"),
            ("assumed_value", "R2"),
            ("value_not_found", "R1"),
        ]
    ]
    assert [w["code"] for w in ordered(warnings)] == [
        "source_open_loop",
        "value_not_found",
        "assumed_value",
    ]


def test_threads_default_to_half_cpu_and_allow_override(monkeypatch):
    monkeypatch.delenv("CIRCUIT_THREADS", raising=False)
    import circuit_sim.backend.inference as inference

    monkeypatch.setattr(inference, "load_config", lambda: {"inference": {"threads": None}})
    monkeypatch.setattr(inference.os, "cpu_count", lambda: 12)
    assert thread_count() == 6
    monkeypatch.setenv("CIRCUIT_THREADS", "3")
    assert thread_count() == 3


def test_reader_wait_is_cancellable_without_swallowing(monkeypatch):
    def cancel():
        raise Cancelled()

    with pytest.raises(Cancelled):
        text.read_text(np.full((50, 50, 3), 255, np.uint8), check=cancel)
