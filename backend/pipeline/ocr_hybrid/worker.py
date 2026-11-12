"""Cached OCR processes with enforceable native-call deadlines and partial evidence."""

import atexit
import importlib
import json
import logging
import multiprocessing
import os
import threading
import time
from types import SimpleNamespace


class WorkerFailure(RuntimeError):
    def __init__(self, message, readings=()):
        super().__init__(message)
        self.readings = list(readings)


def _worker_main(connection, engine_name, config):
    """Own models only in this process, never also in the API process."""
    try:
        os.environ["CIRCUIT_THREADS"] = str(config["threads"])
        from .rapidocr_adapter import RapidOCRAdapter
        from .bangla_adapter import BanglaAdapter, local_reader
        from ...config import resolve_path
        from .router import Run

        if engine_name == "rapidocr":
            engine = RapidOCRAdapter(config.get("rapidocr"))
            engine.get_engine()
        else:
            directory = config.get("bangla", {}).get("model_directory")
            reader = local_reader(str(resolve_path(directory)) if directory else None)
            engine = BanglaAdapter(config.get("bangla"), reader=reader)
        connection.send(("ready", None))
        while True:
            image, boxes, deadline = connection.recv()
            components = [SimpleNamespace(bbox=box) for box in boxes] if boxes else None
            diagnostics = {}
            run = Run(
                deadline,
                lambda: None,
                diagnostics,
                publish=lambda rows: connection.send(("partial", rows)),
            )
            try:
                readings = engine.extract(image, run, components)
                connection.send(("done", (readings, diagnostics)))
            except Exception as exc:
                connection.send(("error", f"{type(exc).__name__}: {exc}"))
    except (EOFError, BrokenPipeError, OSError):
        pass
    except Exception as exc:
        try:
            connection.send(("error", f"{type(exc).__name__}: {exc}"))
        except (EOFError, BrokenPipeError, OSError):
            pass
    finally:
        connection.close()


class OCRWorker:
    def __init__(self, name, config, target=None):
        self.name, self.config, self.target = name, config, target
        self.lock = threading.Lock()
        self.process = self.connection = None
        self.ready = False
        self.stopping = threading.Event()
        self.rewarming = None

    def _check_stopping(self):
        if self.stopping.is_set():
            raise RuntimeError("OCR worker is shutting down")

    def close(self):
        process, connection = self.process, self.connection
        self.process = self.connection = None
        self.ready = False
        if process is not None:
            if process.is_alive():
                process.terminate()
            process.join(timeout=0.15)
            if process.is_alive():
                process.kill()
                process.join(timeout=0.15)
            if not process.is_alive():
                process.close()
        if connection is not None:
            connection.close()

    def _start(self):
        if self.process is not None and self.process.is_alive():
            return
        self.close()
        context = multiprocessing.get_context("spawn")
        self.connection, child = context.Pipe()
        target = self.target or _worker_main
        if self.target is None and __package__.startswith("circuit_sim."):
            # A renamed source checkout uses bootstrap's package alias. Spawn
            # must import a physical package; installed distributions use the
            # canonical package instead. Both receive only arrays/plain boxes.
            try:
                target = importlib.import_module("backend.pipeline.ocr_hybrid.worker")._worker_main
            except ModuleNotFoundError:
                pass
        self.process = context.Process(
            target=target, args=(child, self.name, self.config), daemon=True
        )
        self.process.start()
        child.close()

    def _receive(self, deadline, check):
        while time.monotonic() < deadline:
            self._check_stopping()
            check()
            if self.connection.poll(min(0.025, max(0, deadline - time.monotonic()))):
                try:
                    return self.connection.recv()
                except (EOFError, OSError) as exc:
                    raise WorkerFailure("OCR process exited") from exc
            if not self.process.is_alive():
                raise WorkerFailure("OCR process exited")
        check()
        return "timeout", None

    def _ready(self, deadline, check):
        self._start()
        if self.ready:
            return True
        status, data = self._receive(deadline, check)
        if status == "ready":
            self.ready = True
            return True
        if status == "timeout":
            self.close()
            return False
        raise WorkerFailure(str(data))

    def warmup(self, timeout=60):
        with self.lock:
            try:
                self._check_stopping()
                if not self._ready(time.monotonic() + timeout, self._check_stopping):
                    raise TimeoutError(f"{self.name} model startup timed out")
            except BaseException:
                self.close()
                raise

    def rewarm(self):
        if self.stopping.is_set() or (self.rewarming and self.rewarming.is_alive()):
            return

        def prepare():
            try:
                self.warmup()
            except Exception as exc:
                logging.getLogger(__name__).warning("%s restart failed: %s", self.name, exc)

        self.rewarming = threading.Thread(
            target=prepare, name="ocr-rewarm-" + self.name, daemon=True
        )
        self.rewarming.start()

    def extract(self, image, components, run):
        readings = []
        acquired = False
        try:
            while run.available():
                if self.lock.acquire(timeout=min(0.025, max(0, run.deadline - time.monotonic()))):
                    acquired = True
                    break
            if not acquired or not self._ready(run.deadline, run.check):
                run.diagnostics["budget_exceeded"] = True
                run.diagnostics.setdefault("engine_timeouts", []).append(self.name)
                return readings
            boxes = [tuple(c.bbox) for c in components] if components else []
            self.connection.send((image, boxes, run.deadline))
            while True:
                status, data = self._receive(run.deadline, run.check)
                if status == "partial":
                    readings = data
                elif status == "done":
                    readings, diagnostics = data
                    if diagnostics.get("budget_exceeded"):
                        run.diagnostics["budget_exceeded"] = True
                        run.diagnostics.setdefault("engine_timeouts", []).append(self.name)
                    if diagnostics.get("work_limited"):
                        run.diagnostics.setdefault("engine_limits", []).append(self.name)
                    return readings
                elif status == "timeout":
                    run.diagnostics["budget_exceeded"] = True
                    run.diagnostics.setdefault("engine_timeouts", []).append(self.name)
                    self.close()
                    return readings
                else:
                    raise WorkerFailure(str(data), readings)
        except BaseException as exc:
            if acquired:
                self.close()
            if isinstance(exc, WorkerFailure):
                exc.readings = readings
            raise
        finally:
            if acquired:
                self.lock.release()


_registry = {}
_registry_lock = threading.Lock()


def worker_for(name, config):
    from ...inference import thread_count

    config = {**config, "threads": thread_count()}
    serialized = json.dumps(config, sort_keys=True)
    with _registry_lock:
        previous = _registry.get(name)
        if previous is None or previous[0] != serialized:
            if previous:
                previous[1].stopping.set()
                with previous[1].lock:
                    previous[1].close()
            worker = OCRWorker(name, config)
            _registry[name] = (serialized, worker)
        return _registry[name][1]


def warm_hybrid(config):
    for name in ("rapidocr", "easyocr-bn"):
        worker_for(name, config).warmup()


def close_workers():
    with _registry_lock:
        for _, worker in _registry.values():
            worker.stopping.set()
        for _, worker in _registry.values():
            with worker.lock:
                worker.close()
        _registry.clear()


def worker_states():
    with _registry_lock:
        states = {}
        for name, (_, worker) in _registry.items():
            process = worker.process
            try:
                alive = bool(process and process.is_alive())
            except (ValueError, AssertionError):
                alive = False
            states[name] = (
                "ready"
                if worker.ready and alive
                else "warming"
                if alive or (worker.rewarming and worker.rewarming.is_alive())
                else "unavailable"
            )
        return states


atexit.register(close_workers)


class WorkerAdapter:
    def __init__(self, name, config):
        self.name, self.config = name, config

    def extract(self, image, run, components=None):
        worker = worker_for(self.name, self.config)
        try:
            return worker.extract(image, components, run)
        finally:
            if worker.process is None:
                worker.rewarm()
