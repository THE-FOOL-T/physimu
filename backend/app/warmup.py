"""Model readiness is observable; startup never downloads models."""

import logging
import threading
import time
import numpy as np
from ..core.config import load_config

state = {"detector": "warming", "ocr": "warming", "ocr_backend": None, "warmup_seconds": None}
_thread = None


def wait_for_models(check):
    # Startup is queued outside the per-image budget. Cancellation remains live.
    thread = _thread
    while thread is not None and thread.is_alive():
        check()
        thread.join(timeout=0.05)


def warm_models():
    start = time.perf_counter()
    ocr = load_config().get("ocr", {})
    backend = str(ocr.get("backend", "legacy")).strip().lower()
    state["ocr_backend"] = backend
    try:
        from ..domains.circuit.detect import detect

        detect(np.full((96, 96, 3), 255, np.uint8))
        state["detector"] = "ready"
    except FileNotFoundError:
        state["detector"] = "missing_weights"
    except Exception as exc:
        logging.getLogger("circuit_sim.warmup").exception(
            "Detector warmup failed: %s", type(exc).__name__
        )
        state["detector"] = "error"
    try:
        from ..core.text import LOCK, easy_reader

        with LOCK:
            if backend == "hybrid":
                from ..core.ocr_hybrid.worker import warm_hybrid

                warm_hybrid(ocr)
            elif backend == "legacy":
                easy_reader("en")
                easy_reader("bn", False)
            else:
                raise ValueError("Select legacy or hybrid OCR")
        state["ocr"] = "ready"
    except Exception as exc:
        logging.getLogger("circuit_sim.warmup").exception(
            "OCR warmup failed: %s", type(exc).__name__
        )
        import shutil

        state["ocr"] = (
            "ready" if backend == "legacy" and shutil.which("tesseract") else "unavailable"
        )
    state["warmup_seconds"] = round(time.perf_counter() - start, 3)


def start_warmup():
    global _thread
    from pathlib import Path

    state["detector"] = (
        "warming" if Path(load_config()["detector"]["weights"]).is_file() else "missing_weights"
    )
    state["ocr"] = "warming"
    state["ocr_backend"] = str(load_config()["ocr"]["backend"]).strip().lower()
    _thread = threading.Thread(target=warm_models, name="model-warmup", daemon=True)
    _thread.start()
