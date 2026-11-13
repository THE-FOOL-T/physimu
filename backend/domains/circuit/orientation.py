"""Optional crop classifier, gated on measured real-test superiority."""

import json
from pathlib import Path
import cv2
import numpy as np


def features(crop):
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY) if crop.ndim == 3 else crop
    gray = cv2.resize(gray, (24, 24)).astype(np.float32) / 255
    return (1 - gray).ravel()


def classify(crop, model_path, report_path):
    model_path, report_path = Path(model_path), Path(report_path)
    if not model_path.is_file() or not report_path.is_file():
        return None
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if not report.get("real_test_count") or report.get("classifier_accuracy", 0) <= report.get(
        "heuristic_accuracy", 1
    ):
        return None
    model = np.load(model_path, allow_pickle=False)
    distance = ((model["centroids"] - features(crop)) ** 2).mean(axis=1)
    index = int(np.argmin(distance))
    label = int(model["labels"][index])
    confidence = float(np.exp(-float(distance[index]) * 10))
    if confidence < 0.7:
        return None
    return {
        "orientation_deg": (label // 2) * 90,
        "positive_first": label % 2 == 0,
        "confidence": confidence,
    }
