import io
import json

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from circuit_sim.backend.app.main import app


@pytest.mark.parametrize("endpoint", ["/api/analyze", "/api/analyze/start"])
@pytest.mark.parametrize("page", ["bad", "1.5", "-1"])
def test_malformed_page_keeps_machine_readable_error(endpoint, page):
    response = TestClient(app).post(
        endpoint, files={"image": ("x.pdf", b"%PDF-")}, data={"page": page}
    )
    assert response.status_code == 422
    assert response.json()["detail"] == {
        "code": "invalid_page",
        "message_key": "error.invalid_page",
    }


def test_pdf_page_out_of_range_is_rejected_before_starting_job():
    pdf = io.BytesIO()
    Image.new("RGB", (100, 100), "white").save(pdf, format="PDF")
    response = TestClient(app).post(
        "/api/analyze/start",
        files={"image": ("x.pdf", pdf.getvalue())},
        data={"page": "1"},
    )
    assert response.status_code == 422
    assert response.json()["detail"] == {
        "code": "invalid_page",
        "message_key": "error.invalid_page",
    }


def test_missing_weights_health_and_warmup_without_model_import(monkeypatch, tmp_path):
    monkeypatch.setenv("CIRCUIT_OCR_BACKEND", "legacy")
    from circuit_sim.backend.app import warmup
    from circuit_sim.backend.pipeline import detect, text
    from circuit_sim.backend.app.main import health

    monkeypatch.setenv("CIRCUIT_MODEL", str(tmp_path / "missing.pt"))
    monkeypatch.setattr(warmup, "state", dict(warmup.state))
    monkeypatch.setattr(text, "easy_reader", lambda *args: object())
    detect.detector.cache_clear()
    try:
        with pytest.raises(FileNotFoundError):
            detect.detector()
        warmup.warm_models()
        assert warmup.state["detector"] == "missing_weights"
        assert warmup.state["ocr"] == "ready"
        assert health()["detector_available"] is False
    finally:
        detect.detector.cache_clear()


def test_failed_smoke_writes_unknown_timings_instead_of_crashing(monkeypatch, tmp_path):
    from circuit_sim.backend.tools import smoke

    monkeypatch.setattr(smoke, "ROOT", tmp_path)
    (tmp_path / "docs").mkdir()
    smoke.write_report(
        [
            {
                "image": "unreachable.png",
                "simulation_produced": False,
                "error": "ConnectError",
            }
        ],
        {},
    )
    report = json.loads((tmp_path / "docs/smoke_summary.json").read_text(encoding="utf-8"))
    assert report["produced"] == 0
    assert report["median_seconds"] is None
    assert report["end_to_end_accuracy"] is None
    assert "unmeasured" in (tmp_path / "docs/performance.md").read_text(encoding="utf-8")


@pytest.mark.parametrize("flat", [False, True], ids=["opencv4", "flat-segments"])
def test_line_consumers_accept_both_hough_array_layouts(monkeypatch, flat):
    import cv2
    import numpy as np
    from circuit_sim.backend.pipeline.style import estimate_style
    from circuit_sim.backend.pipeline.annotations import dashed_mask

    image = np.full((200, 200, 3), 255, np.uint8)
    for start in range(10, 190, 16):
        cv2.line(image, (start, 100), (start + 7, 100), (0, 0, 0), 1)
    segments = np.array([[10, 100, 193, 100]], dtype=np.int32)
    monkeypatch.setattr(
        cv2, "HoughLinesP", lambda *a, **k: segments if flat else segments[:, None, :]
    )
    assert estimate_style(image)["style"] in {"printed", "handwritten", "photo"}
    mask = dashed_mask(255 - cv2.cvtColor(image, cv2.COLOR_BGR2GRAY))
    assert mask[100, 30] > 0
