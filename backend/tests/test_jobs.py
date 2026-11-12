import threading
import time
import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient
from circuit_sim.backend.app.main import app
from circuit_sim.backend.app.jobs import JobStore
from circuit_sim.backend.pipeline import engine


def test_real_stage_progress_cap_cancel_and_ttl():
    store = JobStore(limit=1, ttl=0.1)
    gate = threading.Event()

    def runner(progress):
        progress("detect", {"components": [{"id": "R1"}]})
        gate.wait(1)
        progress("solve")
        return {"provenance": "extracted"}

    id_ = store.start(runner)
    try:
        for _ in range(50):
            if store.get(id_)["stage"] == "detect":
                break
            time.sleep(0.002)
        assert store.get(id_)["partial"]["components"][0]["id"] == "R1"
        with pytest.raises(OverflowError):
            store.start(runner)
        store.cancel(id_)
        gate.set()
        for _ in range(50):
            if not store.active:
                break
            time.sleep(0.002)
        assert store.get(id_)["error"]["code"] == "cancelled"
        time.sleep(0.12)
        with pytest.raises(KeyError):
            store.get(id_)
    finally:
        gate.set()
        store.executor.shutdown(wait=True)


@pytest.mark.parametrize(
    "filename,data,page,status,code",
    [
        ("x.txt", b"text", 0, 415, "unsupported_type"),
        ("x.png", b"broken", 0, 415, "undecodable"),
        ("x.pdf", b"%PDF-", -1, 422, "invalid_page"),
        ("x.png", b"x" * (20 * 1024 * 1024 + 1), 0, 413, "too_large"),
    ],
    ids=["unsupported", "undecodable", "invalid-page", "oversized"],
)
def test_upload_validation_codes(filename, data, page, status, code):
    response = TestClient(app).post(
        "/api/analyze/start", files={"image": (filename, data)}, data={"page": page}
    )
    assert response.status_code == status
    assert response.json()["detail"]["code"] == code


def test_job_api_missing_detector_is_separate_demo(monkeypatch):
    def missing(*a, **k):
        raise FileNotFoundError()

    monkeypatch.setattr(engine, "detect", missing)
    from circuit_sim.backend.pipeline import text

    monkeypatch.setattr(text, "read_text", lambda *a, **k: ([], []))
    image = cv2.imencode(".png", np.full((100, 150, 3), 255, np.uint8))[1].tobytes()
    client = TestClient(app)
    response = client.post("/api/analyze/start", files={"image": ("x.png", image)})
    assert response.status_code == 200
    assert response.json()["width"] == 150
    id_ = response.json()["job_id"]
    for _ in range(100):
        job = client.get("/api/analyze/" + id_).json()
        if job["result"] or job["error"]:
            break
        time.sleep(0.01)
    assert job["result"]["provenance"] == "demo_fallback"
    assert job["result"]["netlist"]["image"]["path"] == ""
    assert job["history"] == [
        "queued",
        "received",
        "preprocess",
        "detect",
        "text",
        "solve",
        "done",
    ]
    assert client.delete("/api/analyze/" + id_).json()["cancelled"]
