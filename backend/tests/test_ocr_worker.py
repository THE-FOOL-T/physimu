"""Real spawned-process timeout/cancellation regressions without model dependencies."""

import os
import time
import numpy as np
import pytest
from backend.app.jobs import Cancelled
from backend.pipeline.ocr_hybrid.router import Run
from backend.pipeline.ocr_hybrid.worker import OCRWorker, WorkerFailure


def fake_native_worker(connection, name, config):
    if config.get("mode") == "crash":
        os._exit(17)
    connection.send(("ready", None))
    try:
        while True:
            connection.recv()
            rows = [{"text": "6 V", "engine": name}]
            connection.send(("partial", rows))
            if config.get("mode") == "stall":
                time.sleep(30)
            elif config.get("mode") == "error":
                connection.send(("error", "native failure"))
            else:
                connection.send(
                    (
                        "done",
                        (rows, {"work_limited": True} if config.get("mode") == "limited" else {}),
                    )
                )
    except EOFError:
        pass
    finally:
        connection.close()


def test_native_timeout_keeps_completed_readings_stops_process_and_can_restart():
    worker = OCRWorker("rapidocr", {"mode": "stall"}, target=fake_native_worker)
    try:
        worker.warmup()
        run = Run(time.monotonic() + 0.25, lambda: None, {})
        started = time.monotonic()
        rows = worker.extract(np.zeros((32, 32, 3), np.uint8), None, run)
        assert time.monotonic() - started < 1.5
        assert rows == [{"text": "6 V", "engine": "rapidocr"}]
        assert run.diagnostics["engine_timeouts"] == ["rapidocr"]
        assert worker.process is None and not worker.lock.locked()
        worker.config["mode"] = "ready"
        worker.warmup()
        run = Run(time.monotonic() + 2, lambda: None, {})
        assert worker.extract(np.zeros((32, 32, 3), np.uint8), None, run) == rows
        assert not run.diagnostics
    finally:
        worker.close()


def test_cancel_interrupts_native_work_and_releases_serialization():
    worker = OCRWorker("easyocr-bn", {"mode": "stall"}, target=fake_native_worker)
    try:
        worker.warmup()
        cancel_at = time.monotonic() + 0.15

        def check():
            if time.monotonic() >= cancel_at:
                raise Cancelled()

        with pytest.raises(Cancelled):
            worker.extract(np.zeros((32, 32, 3), np.uint8), None, Run(cancel_at + 20, check, {}))
        assert worker.process is None and not worker.lock.locked()
    finally:
        worker.close()


def test_process_failure_keeps_partial_evidence_and_never_reuses_bad_process():
    worker = OCRWorker("rapidocr", {"mode": "error"}, target=fake_native_worker)
    try:
        worker.warmup()
        with pytest.raises(WorkerFailure) as error:
            worker.extract(
                np.zeros((32, 32, 3), np.uint8), None, Run(time.monotonic() + 2, lambda: None, {})
            )
        assert error.value.readings == [{"text": "6 V", "engine": "rapidocr"}]
        assert worker.process is None
    finally:
        worker.close()


def test_worker_crash_is_reported_and_reaped():
    worker = OCRWorker("rapidocr", {"mode": "crash"}, target=fake_native_worker)
    try:
        with pytest.raises(WorkerFailure):
            worker.warmup()
        assert worker.process is None
    finally:
        worker.close()


def test_cooperative_limit_preserves_completed_readings_and_the_loaded_process():
    worker = OCRWorker("easyocr-bn", {"mode": "limited"}, target=fake_native_worker)
    try:
        worker.warmup()
        pid = worker.process.pid
        for _ in range(2):
            run = Run(time.monotonic() + 2, lambda: None, {})
            assert worker.extract(np.zeros((32, 32, 3), np.uint8), None, run)
            assert run.diagnostics["engine_limits"] == ["easyocr-bn"]
            assert worker.ready and worker.process.pid == pid and worker.process.is_alive()
    finally:
        worker.close()
