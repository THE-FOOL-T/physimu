"""Cold startup and concurrent uploads queue before the page budget starts."""

import threading
import time
import pytest
from circuit_sim.backend.app import analysis, warmup
from circuit_sim.backend.app.jobs import JobStore


def test_startup_waits_for_real_warmup_thread_before_entering_pipeline(monkeypatch):
    monkeypatch.setenv("CIRCUIT_OCR_BACKEND", "hybrid")
    gate = threading.Event()
    thread = threading.Thread(target=lambda: gate.wait(2))
    monkeypatch.setattr(warmup, "_thread", thread)
    thread.start()
    timer = threading.Timer(0.1, gate.set)
    timer.start()
    stages = []

    def analyze(*a, **k):
        assert not thread.is_alive()
        return {"netlist": {"warnings": []}, "solution": {"warnings": []}, "warnings": []}

    monkeypatch.setattr(analysis, "analyze_page", analyze)
    try:
        analysis.run_analysis(None, None, "en", "auto", progress=lambda stage: stages.append(stage))
        assert "queued" in stages
        assert not analysis.HYBRID_ANALYSIS_LOCK.locked()
    finally:
        gate.set()
        thread.join()
        timer.join()


def test_waiting_hybrid_upload_is_cancellable_without_starting_another_pipeline(monkeypatch):
    monkeypatch.setenv("CIRCUIT_OCR_BACKEND", "hybrid")
    monkeypatch.setattr(warmup, "_thread", None)
    monkeypatch.setattr(
        analysis, "analyze_page", lambda *a, **k: pytest.fail("Cancelled queued upload ran")
    )
    store = JobStore(limit=1)
    analysis.HYBRID_ANALYSIS_LOCK.acquire()
    try:
        id_ = store.start(
            lambda progress: analysis.run_analysis(None, None, "en", "auto", progress=progress)
        )
        for _ in range(50):
            if store.get(id_)["stage"] == "queued" and "received" in store.get(id_)["history"]:
                break
            time.sleep(0.01)
        store.cancel(id_)
        store.jobs[id_]["future"].result(timeout=2)
        assert store.get(id_)["error"]["code"] == "cancelled"
    finally:
        analysis.HYBRID_ANALYSIS_LOCK.release()
        store.executor.shutdown(wait=True)
