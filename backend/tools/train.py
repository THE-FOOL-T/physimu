"""Fine-tune v2 and a standard pretrained control into new run directories."""

import argparse
import json
import time
from pathlib import Path
import yaml
from ..pipeline.detect import detector, ROOT


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data", required=True)
    p.add_argument("--control", default=str(ROOT / "models/yolo26n.pt"))
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--device", default="cpu")
    p.add_argument("--execute", action="store_true")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--imgsz", type=int, default=960)
    p.add_argument("--resume")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--out", default=str(ROOT / "models/v3"))
    args = p.parse_args()
    data = Path(args.data).resolve()
    manifest = data.parent / "manifest.json"
    if not manifest.is_file():
        p.error("Use merge_dataset first; checked original-training manifest is required")
    checked = json.loads(manifest.read_text(encoding="utf-8"))
    if not checked.get("original_training_count"):
        p.error("Original training data must be present")
    if not checked.get("near_duplicate_check") or not checked.get("frozen_test_count"):
        p.error("Frozen-test near-duplicate audit is required")
    if checked.get("synthetic_training_fraction", 1) > 0.5:
        p.error("Synthetic training fraction must be <= 50%")
    if args.imgsz not in range(960, 1025):
        p.error("Use 960–1024 pixels")
    if args.smoke:
        args.epochs = 1
    if not args.smoke and not checked.get("human_completeness_review"):
        p.error(
            "Human label-completeness review is required for full training. --smoke is plumbing only."
        )
    names = yaml.safe_load(data.read_text(encoding="utf-8"))["names"]
    if names[:4] != ["resistor", "voltage_source", "capacitor", "switch"]:
        p.error("First four class names must preserve v2")
    plan = {
        "data": str(data),
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "lr0": 0.001,
        "freeze": 0,
        "device": args.device,
        "seed": args.seed,
        "smoke_only": args.smoke,
        "candidates": [str(ROOT / "models/v2_original.pt"), args.control],
        "selection": "Frozen 99-image per-class recall; never train on the test set. Smoke candidates are not eligible for selection.",
    }
    print(json.dumps(plan, indent=2))
    if not args.execute:
        return
    import torch

    torch.set_num_threads(1)
    from ultralytics import YOLO

    out = Path(args.out).resolve()
    if not out.is_relative_to(ROOT):
        p.error("Training output must stay inside this repository")
    out.mkdir(parents=True, exist_ok=True)
    for name, weights in [
        ("v2_finetune", str(ROOT / "models/v2_original.pt")),
        ("pretrained_control", args.control),
    ]:
        start = time.perf_counter()
        model = YOLO(args.resume or weights)
        result = model.train(
            data=str(data),
            epochs=args.epochs,
            imgsz=args.imgsz,
            lr0=0.001,
            freeze=0,
            seed=args.seed,
            device=args.device,
            project=str(out),
            name=name,
            exist_ok=False,
            workers=0,
            batch=1,
            resume=bool(args.resume),
            hsv_h=0,
            hsv_s=0,
            hsv_v=0.05,
            degrees=5,
            translate=0.05,
            scale=0.2,
            fliplr=0,
            flipud=0,
            mosaic=0.5,
            plots=False,
        )
        directory = Path(result.save_dir)
        (directory / "MODEL_CARD.md").write_text(
            "# Candidate model\n\n" + json.dumps(plan, indent=2) + "\n\n"
            "Training metrics are in results.csv. Independent printed/handwritten recall must be measured "
            "before selecting this candidate. Source checkpoint: " + weights + "\n",
            encoding="utf-8",
        )
        (directory / "timing.json").write_text(
            json.dumps({"seconds": time.perf_counter() - start, "plan": plan}, indent=2)
        )
        if args.resume:
            break


if __name__ == "__main__":
    main()
