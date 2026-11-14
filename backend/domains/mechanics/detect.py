"""Local-only, independently cached mechanics detector. Boxes are not geometry."""

from dataclasses import dataclass, asdict
import gc
import hashlib
import os
from pathlib import Path
import threading

import numpy as np
import yaml

from ...core import configure_threads, register_model_release, model_lease
from .config import mechanics_config, ROOT

NAMES = tuple(yaml.safe_load((ROOT / "data/mechanics_class_schema.yaml").read_text())["names"])
_lock = threading.RLock()
_cache = {}


class WeightsUnavailable(RuntimeError):
    code = "weights_unavailable"


@dataclass
class Detection:
    id: str
    type: str
    bbox: list[float]
    confidence: float = 1.0

    def as_dict(self):
        return asdict(self)


def release():
    with _lock:
        _cache.clear()


register_model_release("mechanics", release)


def detector():
    cfg = mechanics_config()
    path = Path(cfg["weights"])
    if not path.is_file() or path.suffix.lower() != ".pt":
        raise WeightsUnavailable("Mechanics weights unavailable; use local authoring.")
    key = ("mechanics", str(path.resolve()), path.stat().st_mtime_ns, path.stat().st_size)
    if key not in _cache:
        release()
        gc.collect()
        configure_threads()
        os.environ["YOLO_OFFLINE"] = "true"
        os.environ.setdefault("YOLO_CONFIG_DIR", str(ROOT / ".cache/ultralytics"))
        from ultralytics import YOLO

        try:
            model = YOLO(str(path))
            if tuple(model.names[i] for i in range(len(model.names))) != NAMES:
                raise ValueError("Expected the independent 21-class mechanics checkpoint")
        except Exception as error:
            raise WeightsUnavailable(
                "Mechanics checkpoint is incompatible or unreadable."
            ) from error
        _cache[key] = model
    return _cache[key], cfg


def detect(image, check=lambda: None):
    with model_lease("mechanics", check), _lock:
        check()
        model, cfg = detector()
        output = model.predict(
            image,
            imgsz=cfg["input_size"],
            conf=cfg["confidence"],
            device=cfg["device"],
            save=False,
            verbose=False,
        )[0]
        check()
        h, w = image.shape[:2]
        rows = []
        for box in output.boxes:
            a, b, c, d = box.xyxy[0].tolist()
            rect = [max(0.0, a), max(0.0, b), min(float(w), c), min(float(h), d)]
            confidence = float(box.conf[0])
            if (
                not np.isfinite([*rect, confidence]).all()
                or rect[0] >= rect[2]
                or rect[1] >= rect[3]
            ):
                continue
            rows.append((NAMES[int(box.cls[0])], rect, confidence))
        rows.sort(key=lambda r: (r[1][1], r[1][0], r[0]))
        return [
            Detection(f"D{i + 1}", name, rect, conf) for i, (name, rect, conf) in enumerate(rows)
        ]


def checkpoint_readiness(*, load=False):
    """Mechanics-specific inventory; file presence alone never means compatible."""
    cfg = mechanics_config()
    path = Path(cfg["weights"])
    result = dict(
        path=str(path),
        expected_class_count=len(NAMES),
        expected_classes=list(NAMES),
        available=False,
        compatible=None,
        status="missing",
    )
    if not path.is_file() or path.suffix.lower() != ".pt":
        return result
    result.update(available=True, status="unverified")
    key = ("mechanics", str(path.resolve()), path.stat().st_mtime_ns, path.stat().st_size)
    if not load and key not in _cache:
        return result
    try:
        with model_lease("mechanics"), _lock:
            model, _ = detector()
            names = [model.names[i] for i in range(len(model.names))]
        result.update(compatible=True, status="ready", actual_class_count=len(names), classes=names)
        if load:
            result["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    except WeightsUnavailable as error:
        result.update(compatible=False, status="incompatible", reason=str(error))
    return result
