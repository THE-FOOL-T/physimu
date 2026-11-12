"""Persistent backend selection and truthful selected-model startup readiness."""

import shutil
import numpy as np
import pytest

from circuit_sim.backend import config
from circuit_sim.backend.app import warmup
from circuit_sim.backend.pipeline import text, ocr_tiles
from circuit_sim.backend.pipeline.ocr_hybrid import router, rapidocr_adapter, bangla_adapter


@pytest.fixture
def hybrid_config(monkeypatch, tmp_path):
    shutil.copyfile(config.ROOT / "config.example.yaml", tmp_path / "config.example.yaml")
    (tmp_path / "config.local.yaml").write_text("ocr:\n  backend: hybrid\n", encoding="utf-8")
    monkeypatch.setattr(config, "ROOT", tmp_path)
    monkeypatch.delenv("CIRCUIT_OCR_BACKEND", raising=False)


def test_persistent_hybrid_routes_without_environment_flag(monkeypatch, hybrid_config):
    calls = []

    def extract(*args):
        calls.append(args[-1]["backend"])
        return [], []

    monkeypatch.setattr(router, "read_hybrid", extract)
    monkeypatch.setattr(text, "easy_reader", lambda *a: pytest.fail("Legacy OCR selected"))
    diagnostics = {}
    text.read_text(np.zeros((40, 40, 3), np.uint8), diagnostics=diagnostics)
    assert calls == ["hybrid"]
    assert diagnostics["ocr_backend"] == "hybrid"


def test_explicit_legacy_override_wins_over_local_hybrid(monkeypatch, hybrid_config):
    monkeypatch.setenv("CIRCUIT_OCR_BACKEND", "legacy")
    monkeypatch.setattr(router, "read_hybrid", lambda *a: pytest.fail("Hybrid override ignored"))
    monkeypatch.setattr(text.shutil, "which", lambda name: None)
    monkeypatch.setattr(text, "easy_reader", lambda *a: object())
    monkeypatch.setattr(ocr_tiles, "easy_tiles", lambda *a, **k: [])
    assert text.read_text(np.zeros((40, 40, 3), np.uint8)) == ([], [])


@pytest.mark.parametrize("missing_model", [False, True])
def test_warmup_loads_selected_engines_and_never_masks_hybrid_failure(
    monkeypatch, hybrid_config, missing_model
):
    from circuit_sim.backend.pipeline import detect

    calls = []
    monkeypatch.setattr(detect, "detect", lambda *a: ([], []))
    monkeypatch.setattr(warmup, "state", {})
    monkeypatch.setattr(text, "easy_reader", lambda *a: pytest.fail("Legacy warmup selected"))
    monkeypatch.setattr(shutil, "which", lambda name: "tesseract")

    def rapid(self):
        calls.append("rapidocr")
        return object()

    def bangla(directory=None):
        calls.append("easyocr-bn")
        if missing_model:
            raise FileNotFoundError("Local Bengali model missing")
        return object()

    from types import SimpleNamespace
    from circuit_sim.backend.pipeline.ocr_hybrid import worker

    monkeypatch.setattr(
        worker,
        "worker_for",
        lambda name, config: SimpleNamespace(
            warmup=lambda: rapid(None) if name == "rapidocr" else bangla()
        ),
    )
    warmup.warm_models()
    assert calls == ["rapidocr", "easyocr-bn"]
    assert warmup.state["ocr_backend"] == "hybrid"
    assert warmup.state["ocr"] == ("unavailable" if missing_model else "ready")


def test_invalid_backend_does_not_fall_back_to_legacy(monkeypatch, hybrid_config):
    monkeypatch.setenv("CIRCUIT_OCR_BACKEND", "invalid")
    monkeypatch.setattr(text, "easy_reader", lambda *a: pytest.fail("Silent legacy fallback"))
    diagnostics = {}
    readings, warnings = text.read_text(np.zeros((40, 40, 3), np.uint8), diagnostics=diagnostics)
    assert readings == []
    assert ("ocr_failed", None) in warnings
    assert diagnostics["ocr_backend"] == "invalid"
