"""Conservative spatial/semantic fusion adapted from MultiOCRRouter.

Engines execute independently. Raw scores only break ties within one engine;
they are never treated as calibrated votes across engines.
"""

import copy
import math
import time

import cv2
import numpy as np

from ..ocr_regions import area, intersection, failure, clean_strokes
from .normalize import normalize, parse, explicit
from .rapidocr_adapter import RapidOCRAdapter
from .bangla_adapter import BanglaAdapter
from .symbols import PhysicsSymbolCandidateResolver


class Run:
    def __init__(self, deadline, check, diagnostics, publish=None):
        self.deadline, self.check, self.diagnostics = deadline, check, diagnostics
        self.publish = publish

    def emit(self, readings):
        if self.publish:
            self.publish(readings)

    def available(self):
        self.check()
        if time.monotonic() >= self.deadline:
            self.diagnostics["budget_exceeded"] = True
            return False
        return True


def same_region(a, b):
    x, y = a["bbox"], b["bbox"]
    av, bv = parse(a["text"]), parse(b["text"])
    if av and bv and av["label"] and bv["label"] and av["label"] != bv["label"]:
        return False
    shared = intersection(x, y)
    aa, ba = max(1, area(x)), max(1, area(y))
    iou = shared / max(1, aa + ba - shared)
    centers_close = all(
        abs((x[i] + x[i + 2] - y[i] - y[i + 2]) / 2)
        <= max(3, min(x[i + 2] - x[i], y[i + 2] - y[i]) * 0.3)
        for i in (0, 1)
    )
    identical = normalize(a["text"]).replace(" ", "") == normalize(b["text"]).replace(" ", "")
    return centers_close and (iou >= 0.65 or (identical and shared / min(aa, ba) >= 0.85))


def rank(item):
    v = parse(item["text"])
    return 3 if explicit(item) else 2 if v and v["label"] else 1 if v else 0


def fuse(items):
    groups = []
    for item in items:
        # Complete-link grouping avoids chaining a broad box across two labels.
        group = next((g for g in groups if all(same_region(item, other) for other in g)), None)
        if group is None:
            groups.append([item])
        else:
            group.append(item)
    result = []
    for group in groups:
        # Semantic rank first. Fixed provider order for ties across engines.
        engines = list(dict.fromkeys(i.get("engine", "") for i in group))
        selected = max(
            group,
            key=lambda i: (rank(i), -engines.index(i.get("engine", "")), i.get("confidence", 0)),
        )
        item = copy.deepcopy(selected)
        item["alternatives"] = copy.deepcopy(selected.get("alternatives", []))
        for other in group:
            if other is not selected:
                item["alternatives"].append(copy.deepcopy(other))
        for alternative in item["alternatives"]:
            alternative["parsed"] = parse(alternative["text"])
        item["provenance"] = list(dict.fromkeys(i.get("engine", "unknown") for i in group))
        values = [
            v
            for i in [item, *item["alternatives"]]
            if i.get("confidence", 0) >= 0.65
            and (v := parse(i["text"]))
            and v["number"] is not None
        ]
        item["ocr_conflict"] = (
            any(
                not math.isclose(v["number"], values[0]["number"], rel_tol=1e-6, abs_tol=1e-12)
                or (v["unit"] and values[0]["unit"] and v["unit"] != values[0]["unit"])
                for v in values[1:]
            )
            if values
            else False
        )
        PhysicsSymbolCandidateResolver().enrich(item)
        result.append(item)
    return sorted(result, key=lambda i: (i["bbox"][1], i["bbox"][0]))


class MultiOCRRouter:
    def __init__(self, config=None, primary=None, bangla=None):
        from .worker import WorkerAdapter

        config = config or {}
        self.engines = [
            primary or WorkerAdapter("rapidocr", config),
            bangla or WorkerAdapter("easyocr-bn", config),
        ]

    def extract(self, image, *, components=None, diagnostics, deadline, check):
        items, available = [], 0
        for index, engine in enumerate(self.engines):
            run = Run(deadline, check, diagnostics)
            if not run.available():
                break
            # Each native engine is isolated and can be stopped at this limit.
            engine_end = min(
                deadline,
                time.monotonic()
                + max(0, deadline - time.monotonic()) / (len(self.engines) - index),
            )
            started = time.monotonic()
            try:
                output = engine.extract(image, Run(engine_end, check, diagnostics), components)
                check()
                items.extend(output)
                available += 1
                diagnostics.setdefault("stages", []).append(
                    {
                        "stage": engine.name,
                        "status": "timeout"
                        if engine.name in diagnostics.get("engine_timeouts", [])
                        else "limited"
                        if engine.name in diagnostics.get("engine_limits", [])
                        else "ready",
                        "readings": len(output),
                        "seconds": time.monotonic() - started,
                    }
                )
            except Exception as exc:
                items.extend(getattr(exc, "readings", []))
                failure(diagnostics, engine.name, exc)
        diagnostics["engine_readings"] = copy.deepcopy(items)
        result = fuse(items)
        # Preserve wire evidence without changing prepare_trace. Low-confidence,
        # bare or conflicting hybrid boxes are never erasure authority.
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
        _, removed = clean_strokes(image)
        for item in result:
            x, y, right, bottom = [int(v) for v in item["bbox"]]
            ink = gray[y:bottom, x:right] < 180
            overlap = (
                np.count_nonzero(removed[y:bottom, x:right]) / max(1, np.count_nonzero(ink)) > 0.2
            )
            item["wire_overlap"] = bool(
                overlap
                or item.get("ocr_conflict")
                or not explicit(item)
                or item["confidence"] < 0.65
            )
        warnings = []
        if not available:
            warnings.append(("ocr_unavailable", None))
        if any(
            s["status"] in {"failed", "timeout", "limited"} for s in diagnostics.get("stages", [])
        ):
            warnings.append(("ocr_partial" if available else "ocr_failed", None))
        if diagnostics.get("budget_exceeded") or time.monotonic() >= deadline:
            warnings.append(("time_budget", None))
        return result, warnings


def read_hybrid(image, components, diagnostics, deadline, check, lock, config):
    run = Run(deadline, check, diagnostics)
    acquired = False
    try:
        while run.available():
            if lock.acquire(timeout=min(0.05, max(0, deadline - time.monotonic()))):
                acquired = True
                break
        if not acquired:
            return [], [("time_budget", None)]
        return MultiOCRRouter(config).extract(
            image, components=components, diagnostics=diagnostics, deadline=deadline, check=check
        )
    finally:
        if acquired:
            lock.release()
