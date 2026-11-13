"""Common mechanics per-class protocol. Synthetic scores are never real accuracy."""

import argparse
from collections import Counter
import json
from pathlib import Path
import time

import numpy as np
from PIL import Image

from .common import (
    NAMES,
    ARCHETYPES,
    ROOT,
    contained,
    load_dataset,
    relative_file,
    read_labels,
    sha256,
    write_json,
)
from .gold import verify_frozen


def iou(a, b):
    area = max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))
    return area / max(1e-12, (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - area)


def ap101(tp, fp, support):
    if not support:
        return None
    recall = np.cumsum(tp) / support
    precision = np.cumsum(tp) / np.maximum(1, np.cumsum(tp) + np.cumsum(fp))
    return float(
        np.mean([np.max(precision[recall >= r], initial=0) for r in np.linspace(0, 1, 101)])
    )


def score(ground, predictions, *, confidence=0.25):
    if not 0 <= confidence <= 1:
        raise ValueError("Confidence must be in [0,1]")
    if set(ground) != set(predictions):
        raise ValueError("Prediction/image set mismatch")
    result = {}
    for cls, name in enumerate(NAMES):
        support = sum(c == cls for rows in ground.values() for c, _ in rows)
        records = sorted(
            [
                (float(conf), key, box)
                for key, rows in predictions.items()
                for c, conf, box in rows
                if c == cls
            ],
            key=lambda v: -v[0],
        )
        aps = []
        tp50 = []
        fp50 = []
        for threshold in np.linspace(0.5, 0.95, 10):
            used = set()
            tp = []
            fp = []
            for conf, key, box in records:
                overlap, j = max(
                    [
                        (iou(box, g), j)
                        for j, (c, g) in enumerate(ground[key])
                        if c == cls and (key, j) not in used
                    ],
                    default=(0, -1),
                )
                hit = overlap >= threshold
                if hit:
                    used.add((key, j))
                tp.append(int(hit))
                fp.append(int(not hit))
            aps.append(ap101(tp, fp, support))
            if threshold == 0.5:
                tp50, fp50 = tp, fp
        kept = [i for i, row in enumerate(records) if row[0] >= confidence]
        hits = sum(tp50[i] for i in kept)
        false = sum(fp50[i] for i in kept)
        result[name] = {
            "support": support,
            "predictions": len(kept),
            "tp": hits,
            "fp": false,
            "fn": support - hits,
            "precision": hits / len(kept) if kept else (0.0 if support else None),
            "recall": hits / support if support else None,
            "AP50": aps[0],
            "AP50_95": float(np.mean(aps)) if support else None,
        }
    return result


def protocol(imgsz=640, confidence=0.25):
    if imgsz < 32 or imgsz % 32:
        raise ValueError("Image size must be a positive multiple of 32")
    if not 0 <= confidence <= 1:
        raise ValueError("Confidence must be in [0,1]")
    return {
        "imgsz": imgsz,
        "confidence": confidence,
        "ap_confidence_floor": 0.001,
        "nms_iou": 0.7,
        "matching_iou": 0.5,
        "AP_iou_thresholds": [round(float(v), 2) for v in np.linspace(0.5, 0.95, 10)],
        "AP_interpolation_points": 101,
        "max_det": 300,
        "class_order": list(NAMES),
    }


def local_model(weights, *, general=False):
    path = Path(weights).resolve(strict=True)
    if path.suffix != ".pt":
        raise ValueError("Provide a local .pt checkpoint; downloads are disabled")
    # Set before importing the SDK. Never pass a model nickname or remote URL.
    import os

    os.environ["YOLO_OFFLINE"] = "true"
    os.environ.setdefault("YOLO_CONFIG_DIR", str(ROOT / ".cache/mechanics-ultralytics"))
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache/mechanics-matplotlib"))
    import torch

    torch.set_num_threads(2)
    from ultralytics import YOLO

    model = YOLO(str(path))
    names = tuple(model.names[i] for i in range(len(model.names)))
    if any(
        n in names
        for n in ("resistor", "voltage_source", "capacitor", "voltmeter", "ammeter", "switch")
    ):
        raise ValueError("Circuit weights must never initialize mechanics")
    if not general and names != NAMES:
        raise ValueError("Checkpoint class order does not match mechanics")
    if general and names != NAMES and len(names) != 80:
        raise ValueError("Use an 80-class general pretrained checkpoint or a mechanics checkpoint")
    return model


def evaluate(
    root, weights, *, split="val", style=None, imgsz=640, confidence=0.25, device="cpu", model=None
):
    root = Path(root).resolve()
    manifest = load_dataset(root)
    settings = protocol(imgsz, confidence)
    records = [
        r
        for r in manifest["records"]
        if r["split"] == split and (style is None or r.get("style") == style)
    ]
    if not records:
        raise ValueError("No images in the requested evaluation partition")
    model = model or local_model(weights)
    ground = {}
    predictions = {}
    seconds = []
    for row in records:
        image = relative_file(root, row["image"])
        with Image.open(image) as raster:
            w, h = raster.size
        ground[row["image"]] = read_labels(relative_file(root, row["label"]), w, h)
        start = time.perf_counter()
        output = model.predict(
            str(image),
            imgsz=imgsz,
            conf=0.001,
            iou=0.7,
            max_det=300,
            device=device,
            save=False,
            verbose=False,
        )[0]
        seconds.append(time.perf_counter() - start)
        predictions[row["image"]] = [
            (int(b.cls[0]), float(b.conf[0]), b.xyxy[0].tolist()) for b in output.boxes
        ]
    origin = manifest["origin"]
    return {
        "domain": "mechanics",
        "origin": origin,
        "label": {
            "synthetic": "synthetic, not real accuracy",
            "mixed": "mixed synthetic/reviewed real validation, not independent real accuracy",
            "real": "HUMAN-reviewed real labels; verify source-separated frozen membership",
        }[origin],
        "images": len(records),
        "image_sha256": sorted(r["sha256"] for r in records),
        "split": split,
        "style": style or "all",
        "protocol": settings,
        "weights_sha256": sha256(weights),
        "classes": score(ground, predictions, confidence=confidence),
        "seconds": {
            "total": sum(seconds),
            "median": float(np.median(seconds)),
            "p95": float(np.percentile(seconds, 95)),
        },
        "inference_scope": "model.predict wall time per image, including preprocessing and first-call warmup; excludes label/file audit",
        "smoke_only": False,
        "frozen_real": False,
    }


def evaluate_frozen(root, weights, *, style="printed", imgsz=640, confidence=0.25, device="cpu"):
    if style not in {"printed", "handwritten"}:
        raise ValueError("Frozen real metrics are printed/handwritten separately")
    records = [r for r in verify_frozen(root) if r["style"] == style]
    report = {
        "domain": "mechanics",
        "origin": "real",
        "style": style,
        "split": "frozen",
        "frozen_real": bool(records),
        "smoke_only": False,
        "images": len(records),
        "image_sha256": sorted(r["sha256"] for r in records),
        "protocol": protocol(imgsz, confidence),
    }
    if not records or any("labels" not in r for r in records):
        report.update(
            classes={
                name: {key: None for key in ("support", "precision", "recall", "AP50", "AP50_95")}
                for name in NAMES
            },
            seconds=None,
            human_task="Supply independently HUMAN-reviewed frozen images/scenes and detector labels with hashes; no real metric was measured.",
        )
        return report
    model = local_model(weights)
    ground = {}
    predictions = {}
    seconds = []
    for r in records:
        with Image.open(r["image"]) as im:
            w, h = im.size
        ground[r["sha256"]] = read_labels(r["labels"], w, h)
        start = time.perf_counter()
        result = model.predict(
            r["image"],
            imgsz=imgsz,
            conf=0.001,
            iou=0.7,
            max_det=300,
            device=device,
            save=False,
            verbose=False,
        )[0]
        seconds.append(time.perf_counter() - start)
        predictions[r["sha256"]] = [
            (int(b.cls[0]), float(b.conf[0]), b.xyxy[0].tolist()) for b in result.boxes
        ]
    report.update(
        classes=score(ground, predictions, confidence=confidence),
        weights_sha256=sha256(weights),
        seconds={
            "total": sum(seconds),
            "median": float(np.median(seconds)),
            "p95": float(np.percentile(seconds, 95)),
        },
    )
    return report


def quota(root):
    root = Path(root)
    if not (root / "manifest.json").is_file():
        counts = Counter()
        archetypes = Counter()
        n = 0
        present = False
    else:
        m = load_dataset(root)
        if m["origin"] != "real":
            raise ValueError("Real quota reports cannot count synthetic examples")
        counts = Counter()
        archetypes = Counter()
        n = len(m["records"])
        present = True
        for r in m["records"]:
            with Image.open(root / r["image"]) as image:
                counts.update(NAMES[c] for c, _ in read_labels(root / r["label"], *image.size))
            archetypes.update([r["archetype"]])
    return {
        "origin": "real",
        "images": n,
        "reviewed_manifest_present": present,
        "classes": {
            name: {
                "instances": counts[name],
                "minimum_target": 25,
                "preferred_target": 40,
                "minimum_deficit": max(0, 25 - counts[name]),
            }
            for name in NAMES
        },
        "archetypes": {
            name: {
                "images": archetypes[name],
                "target": 10,
                "deficit": max(0, 10 - archetypes[name]),
            }
            for name in ARCHETYPES
        },
        "human_task": "Review weakest classes first; quotas do not establish detector accuracy.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dataset", type=Path)
    p.add_argument("--frozen", type=Path)
    p.add_argument("--weights", type=Path)
    p.add_argument("--quota", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--confidence", type=float, default=0.25)
    p.add_argument("--device", default="cpu")
    p.add_argument("--split", default="val", choices=["train", "val", "test", "pool"])
    p.add_argument("--style")
    args = p.parse_args()
    result = (
        evaluate_frozen(
            args.frozen,
            args.weights,
            style=args.style or "printed",
            imgsz=args.imgsz,
            confidence=args.confidence,
            device=args.device,
        )
        if args.frozen
        else (
            quota(args.quota)
            if args.quota
            else evaluate(
                args.dataset,
                args.weights,
                split=args.split,
                style=args.style,
                imgsz=args.imgsz,
                confidence=args.confidence,
                device=args.device,
            )
        )
    )
    write_json(contained(args.out), result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
