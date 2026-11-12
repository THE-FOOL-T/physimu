"""Lazy CPU YOLO wrapper; original class ids remain unchanged."""

from functools import lru_cache
import os
from pathlib import Path
import threading
import numpy as np
import yaml
from ..config import load_config
from .netlist import Component, Terminal, Value, Polarity

ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("YOLO_CONFIG_DIR", str(ROOT / ".cache/ultralytics"))
LOCK = threading.Lock()


@lru_cache(maxsize=1)
def detector():
    cfg = load_config()["detector"]
    path = Path(os.getenv("CIRCUIT_MODEL", str(ROOT / cfg["weights"])))
    if not path.is_file():
        raise FileNotFoundError("Detector weights unavailable")
    from ..inference import configure_threads

    configure_threads()
    from ultralytics import YOLO

    return YOLO(str(path)), cfg


def detect(image, threshold=None, tiled=False, check=lambda: None):
    model, cfg = detector()
    h, w = image.shape[:2]
    boxes = []
    windows = [(0, 0, w, h)]
    if tiled or cfg.get("tiled"):
        side = 800
        stride = 600
        windows += [
            (x, y, min(w, x + side), min(h, y + side))
            for y in range(0, h, stride)
            for x in range(0, w, stride)
        ]
    with LOCK:
        for x, y, x2, y2 in windows:
            check()
            r = model.predict(
                image[y:y2, x:x2],
                imgsz=cfg["input_size"],
                conf=threshold or cfg["confidence"],
                device=cfg["device"],
                verbose=False,
                save=False,
            )[0]
            for box in r.boxes:
                a, b, c, d = box.xyxy[0].tolist()
                boxes.append(
                    (
                        model.names[int(box.cls[0])],
                        float(box.conf[0]),
                        [a + x, b + y, c + x, d + y],
                    )
                )

    def iou(a, b):
        x = max(0, min(a[2], b[2]) - max(a[0], b[0]))
        y = max(0, min(a[3], b[3]) - max(a[1], b[1]))
        inter = x * y
        return inter / max(
            1e-9, (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
        )

    kept = []
    for b in sorted(boxes, key=lambda b: -b[1]):
        if not any(b[0] == k[0] and iou(b[2], k[2]) > 0.45 for k in kept):
            kept.append(b)
    cs = []
    annotations = []
    counts = {}
    for name, confidence, bbox in sorted(kept, key=lambda b: (b[2][1], b[2][0])):
        if name in {
            "junction",
            "text_label",
            "terminal_marker",
            "plus_minus_mark",
            "arrow",
        }:
            annotations.append({"type": name, "bbox": bbox, "confidence": confidence})
            continue
        kind = {"voltage_source": "dc_source"}.get(name, name)
        prefix = {
            "resistor": "R",
            "dc_source": "V",
            "capacitor": "C",
            "switch": "S",
            "inductor": "L",
        }.get(kind, "X")
        counts[prefix] = counts.get(prefix, 0) + 1
        id_ = prefix + str(counts[prefix])
        x1, y1, x2, y2 = bbox
        vertical = (y2 - y1) > (x2 - x1)
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        if kind in {"dc_source", "battery"}:
            # Battery plates run perpendicular to the electrical leads.
            vertical = not vertical
            if 0.7 < (x2 - x1) / max(1, y2 - y1) < 1.4:
                # Circular source: compare external wire support in four directions.
                import cv2

                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                def ink(a, b, c, d):
                    crop = gray[max(0, int(b)) : min(h, int(d)), max(0, int(a)) : min(w, int(c))]
                    return float(np.mean(crop < 140)) if crop.size else 0

                horizontal = ink(x1 - 12, my - 2, x1, my + 3) + ink(x2, my - 2, x2 + 12, my + 3)
                upright = ink(mx - 2, y1 - 12, mx + 3, y1) + ink(mx - 2, y2, mx + 3, y2 + 12)
                vertical = upright > horizontal
        xy = [(mx, y1), (mx, y2)] if vertical else [(x1, my), (x2, my)]
        terminals = [
            Terminal(id=id_ + suffix, xy=point, node="pending")
            for suffix, point in zip([".a", ".b"], xy)
        ]
        component = Component(
            id=id_,
            type=kind,
            bbox=bbox,
            orientation_deg=90 if vertical else 0,
            terminals=terminals,
            value=Value(
                unit={"dc_source": "V", "capacitor": "F", "inductor": "H"}.get(kind, "ohm")
            ),
            polarity=Polarity(positive_terminal=id_ + ".a")
            if kind in {"dc_source", "battery", "ac_source"}
            else None,
            confidence=confidence,
        )
        if kind in {"dc_source", "battery"}:
            # For a battery, compare the long and short perpendicular plates.
            import cv2

            crop = image[
                max(0, int(y1)) : min(h, int(y2) + 1),
                max(0, int(x1)) : min(w, int(x2) + 1),
            ]
            if crop.size:
                gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 60, 140)
                lines = cv2.HoughLinesP(
                    edges,
                    1,
                    np.pi / 180,
                    threshold=8,
                    minLineLength=max(5, int(min(crop.shape[:2]) * 0.3)),
                    maxLineGap=2,
                )
                plates = []
                for line in np.asarray(lines).reshape(-1, 4) if lines is not None else []:
                    a, b, c, d = line
                    dx = abs(c - a)
                    dy = abs(d - b)
                    if vertical and dx > 3 * max(1, dy):
                        plates.append((dx, (b + d) / 2))
                    elif not vertical and dy > 3 * max(1, dx):
                        plates.append((dy, (a + c) / 2))
                if len(plates) >= 2:
                    longest, position = max(plates)
                    span = crop.shape[0 if vertical else 1]
                    # Only trust a clear plate length difference, not circular arcs.
                    if max(p[0] for p in plates) > 1.25 * min(p[0] for p in plates):
                        component.polarity.positive_terminal = terminals[
                            0 if position < span / 2 else 1
                        ].id
        if kind in {"dc_source", "battery"}:
            from .orientation import classify

            result = None
            if cfg.get("orientation_model") and cfg.get("orientation_report"):
                crop = image[
                    max(0, int(y1)) : min(h, int(y2) + 1),
                    max(0, int(x1)) : min(w, int(x2) + 1),
                ]
                if crop.size:
                    result = classify(
                        crop,
                        ROOT / cfg["orientation_model"],
                        ROOT / cfg["orientation_report"],
                    )
            if result:
                deg = result["orientation_deg"]
                component.orientation_deg = deg
                ends = [(mx, y1), (mx, y2)] if deg % 180 else [(x1, my), (x2, my)]
                if deg in {180, 270}:
                    ends.reverse()
                for terminal, point in zip(component.terminals, ends):
                    terminal.xy = point
                component.polarity.positive_terminal = component.terminals[
                    0 if result["positive_first"] else 1
                ].id
            else:
                component.confidence = min(component.confidence, 0.8)
        if kind == "switch":
            # A closed contact has continuous ink along its lead axis. An open
            # lever leaves a clear central gap. Ambiguous cases keep the default.
            import cv2

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            a, b = terminals[0].xy, terminals[1].xy
            samples = [
                gray[
                    min(h - 1, max(0, int(a[1] + (b[1] - a[1]) * f))),
                    min(w - 1, max(0, int(a[0] + (b[0] - a[0]) * f))),
                ]
                < 150
                for f in np.linspace(0.25, 0.75, 20)
            ]
            if np.mean(samples) < 0.3:
                component.switch_closed = False
        cs.append(component)
    return cs, annotations
