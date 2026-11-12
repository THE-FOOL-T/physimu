import json
from pathlib import Path
import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient
from circuit_sim.backend.app.main import app
from circuit_sim.backend.pipeline import engine
from circuit_sim.backend.pipeline.preprocess import decode, figure_regions
from circuit_sim.backend.pipeline.netlist import Netlist

client = TestClient(app)
ROOT = Path(__file__).resolve().parents[2]


def png():
    return cv2.imencode(".png", np.full((200, 300, 3), 255, np.uint8))[1].tobytes()


def test_health_and_solve():
    assert client.get("/api/health").json()["status"] == "ok"
    net = json.loads((ROOT / "fixtures/series.json").read_text())["netlist"]
    r = client.post("/api/solve", json={"netlist": net, "overrides": {"R1": 4}})
    assert r.status_code == 200
    assert r.json()["solution"]["components"]["R1"]["current"] == pytest.approx(1)
    assert r.headers["x-request-id"]


def test_automatic_fallback_on_detector_absent(monkeypatch):
    def missing(*a, **k):
        raise FileNotFoundError()

    monkeypatch.setattr(engine, "detect", missing)
    from circuit_sim.backend.pipeline import text

    monkeypatch.setattr(text, "read_text", lambda *a, **k: ([], [("ocr_unavailable", None)]))
    r = client.post("/api/analyze", files={"image": ("blank.png", png(), "image/png")})
    assert r.status_code == 200
    data = r.json()
    Netlist.model_validate(data["netlist"])
    assert data["solution"]["components"]
    assert data["source_image"].startswith("data:")
    assert data["netlist"]["meta"]["degraded"]
    assert any(w["code"] == "detector_unavailable" for w in data["warnings"])


def test_reject_invalid_input_and_storage_without_optin():
    assert (
        client.post("/api/analyze", files={"image": ("bad.txt", b"not an image")}).status_code
        == 415
    )
    net = (ROOT / "fixtures/series.json").read_text()
    assert (
        client.post(
            "/api/corrections", files={"image": ("x.png", png())}, data={"netlist": net}
        ).status_code
        == 400
    )


def test_exif_decoder_and_image_limits():
    image = decode(png())
    assert image.shape == (200, 300, 3)
    with pytest.raises(Exception):
        decode(b"x")
