"""Reproducible detector AP and confusion matrix, without writing source datasets."""

import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
from ..pipeline.detect import detector

ROOT = Path(__file__).resolve().parents[2]


def iou(a, b):
    x = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    y = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    v = x * y
    return v / max(1e-12, (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - v)


def ap101(tp, fp, count):
    if not count:
        return None
    recall = np.cumsum(tp) / count
    precision = np.cumsum(tp) / np.maximum(1, np.cumsum(tp) + np.cumsum(fp))
    return float(
        np.mean([np.max(precision[recall >= r], initial=0) for r in np.linspace(0, 1, 101)])
    )


def evaluate(model, images, labels, imgsz=640, class_names=None):
    names = dict(class_names or model.names)
    # Reference vocabularies may contain meters that v2 cannot emit. Map by
    # class NAME so a later expanded model is not evaluated with the wrong IDs.
    for name in model.names.values():
        if name not in names.values():
            names[len(names)] = name
    if sorted(names) != list(range(len(names))):
        raise ValueError("Class ids must be contiguous from zero")
    pred_map = {
        cls: next(i for i, name in names.items() if name == label)
        for cls, label in model.names.items()
    }
    predictions = {}
    gold = {}
    paths = sorted(
        p for p in Path(images).rglob("*") if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    )
    if not paths:
        raise ValueError("No evaluation images; HUMAN-labeled held-out set is required")
    for path in paths:
        label = Path(labels) / (path.stem + ".txt")
        if not label.is_file():
            raise ValueError("Missing reviewed label file: " + str(label))
        with Image.open(path) as im:
            w, h = im.size
        rows = []
        for line in label.read_text(encoding="utf-8").splitlines():
            cls, x, y, bw, bh = map(float, line.split()[:5])
            rows.append(
                (
                    int(cls),
                    [
                        (x - bw / 2) * w,
                        (y - bh / 2) * h,
                        (x + bw / 2) * w,
                        (y + bh / 2) * h,
                    ],
                )
            )
        gold[str(path)] = rows
        r = model.predict(str(path), imgsz=imgsz, conf=0.001, device="cpu", verbose=False)[0]
        predictions[str(path)] = [
            (pred_map[int(b.cls[0])], float(b.conf[0]), b.xyxy[0].tolist()) for b in r.boxes
        ]
    metrics = {}
    confusion = np.zeros((len(names) + 1, len(names) + 1), dtype=int)
    for cls, name in names.items():
        count = sum(c == cls for rows in gold.values() for c, _ in rows)
        records = sorted(
            [
                (confidence, path, box)
                for path, rows in predictions.items()
                for c, confidence, box in rows
                if c == cls
            ],
            reverse=True,
        )
        aps = []
        p50 = r50 = 0
        for threshold in np.arange(0.5, 0.951, 0.05):
            seen = set()
            tp = []
            fp = []
            for confidence, path, box in records:
                candidates = [
                    (iou(box, g), j)
                    for j, (c, g) in enumerate(gold[path])
                    if c == cls and (path, j) not in seen
                ]
                overlap, j = max(candidates, default=(0, -1))
                hit = overlap >= threshold
                if hit:
                    seen.add((path, j))
                tp.append(int(hit))
                fp.append(int(not hit))
            ap = ap101(tp, fp, count)
            if ap is not None:
                aps.append(ap)
            if abs(threshold - 0.5) < 1e-6:
                cutoff = [i for i, r in enumerate(records) if r[0] >= 0.25]
                hits = sum(tp[i] for i in cutoff)
                p50 = hits / max(1, len(cutoff))
                r50 = hits / max(1, count)
        metrics[name] = {
            "gold": count,
            "precision_conf025": p50,
            "recall_conf025": r50,
            "AP50": aps[0] if aps else None,
            "AP50_95": float(np.mean(aps)) if aps else None,
        }
    for path, preds in predictions.items():
        seen = set()
        for cls, confidence, box in sorted(preds, key=lambda x: -x[1]):
            if confidence < 0.25:
                continue
            overlap, j = max(
                [(iou(box, g), j) for j, (_, g) in enumerate(gold[path]) if j not in seen],
                default=(0, -1),
            )
            if overlap >= 0.5:
                seen.add(j)
                confusion[gold[path][j][0], cls] += 1
            else:
                confusion[-1, cls] += 1
        for j, (cls, _) in enumerate(gold[path]):
            if j not in seen:
                confusion[cls, -1] += 1
    return {
        "count": len(paths),
        "classes": metrics,
        "mAP50": float(np.mean([m["AP50"] for m in metrics.values() if m["AP50"] is not None])),
        "mAP50_95": float(
            np.mean([m["AP50_95"] for m in metrics.values() if m["AP50_95"] is not None])
        ),
        "confusion_matrix_rows_gold_columns_predicted": confusion.tolist(),
        "class_order": list(names.values()) + ["background"],
        "imgsz": imgsz,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--weights")
    p.add_argument("--images", required=True)
    p.add_argument("--labels", required=True)
    p.add_argument("--names", help="Reference data.yaml with its class vocabulary")
    p.add_argument("--description")
    p.add_argument("--out", default=str(ROOT / "docs/detector_metrics.json"))
    p.add_argument("--diagnostic-seen", action="store_true")
    args = p.parse_args()
    if args.weights:
        import torch

        torch.set_num_threads(1)
        from ultralytics import YOLO

        model = YOLO(args.weights)
        from ..config import load_config

        cfg = load_config()["detector"]
    else:
        model, cfg = detector()
    class_names = None
    if args.names:
        import yaml

        names = yaml.safe_load(Path(args.names).read_text(encoding="utf-8"))["names"]
        class_names = {
            int(i): str(n)
            for i, n in (enumerate(names) if isinstance(names, list) else names.items())
        }
    result = evaluate(model, args.images, args.labels, cfg["input_size"], class_names)
    result["split"] = args.description or (
        "seen-image regression; NOT held out"
        if args.diagnostic_seen
        else "owner-supplied evaluation set; verify disjointness"
    )
    Path(args.out).write_text(json.dumps(result, indent=2))
    report = "# Detector evaluation\n\n" + result["split"] + "\n\n"
    report += f"{result['count']} images; inference size {result['imgsz']}. AP uses 101-point interpolated precision over IoU .50:.05:.95. Precision/recall use confidence .25.\n\n"
    report += "|Class|Gold|Precision|Recall|AP50|AP50–95|\n|---|---:|---:|---:|---:|---:|\n"
    for name, m in result["classes"].items():
        report += f"|{name}|{m['gold']}|{m['precision_conf025']:.4f}|{m['recall_conf025']:.4f}|{m['AP50'] if m['AP50'] is not None else 'N/A'}|{m['AP50_95'] if m['AP50_95'] is not None else 'N/A'}|\n"
    report += "\nFull confusion matrix and metrics: `" + Path(args.out).name + "`.\n"
    if args.diagnostic_seen:
        report += "\nThe requested independent printed/handwritten baseline remains blocked on HUMAN-labeled, disjoint held-out sets. These values must not be used for model selection.\n"
    Path(args.out).with_suffix(".md").write_text(report, encoding="utf-8")
    print(json.dumps(result, indent=2))
    plot_confusion(result, Path(args.out).with_suffix(".png"))


def plot_confusion(result, path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    matrix = np.array(result["confusion_matrix_rows_gold_columns_predicted"])
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.imshow(matrix, cmap="Blues")
    labels = result["class_order"]
    ax.set(
        xticks=range(len(labels)),
        yticks=range(len(labels)),
        xticklabels=labels,
        yticklabels=labels,
        xlabel="Predicted class",
        ylabel="Gold class",
        title="Detector confusion: "
        + (
            "seen regression (not held out)"
            if "seen-image" in result.get("split", "")
            else "evaluation"
        ),
    )
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right")
    for (i, j), v in np.ndenumerate(matrix):
        ax.text(
            j,
            i,
            str(v),
            ha="center",
            va="center",
            color="white" if v > matrix.max() / 2 else "#263c37",
        )
    fig.tight_layout()
    fig.savefig(path, dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    main()
