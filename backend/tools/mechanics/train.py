"""Paired mechanics fine-tune/control. Local weights only; smoke never qualifies for release."""

import argparse
import json
from pathlib import Path
import shutil
import time

from PIL import Image
import yaml

from .common import ARCHETYPES, NAMES, ROOT, contained, fresh, load_dataset, sha256, write_json
from .eval_detector import evaluate, local_model
from .leakage import audit


def training_plan(
    dataset,
    pretrained,
    output,
    *,
    finetune=None,
    smoke=False,
    device="cpu",
    epochs=50,
    imgsz=640,
    seed=42,
):
    root = Path(dataset).resolve()
    manifest = load_dataset(root)
    out = contained(output)
    if root.is_relative_to(ROOT / "data/eval") or root == out or out.is_relative_to(root):
        raise ValueError("Never train on frozen data or write inside an input dataset")
    weights = Path(pretrained).resolve(strict=True)
    candidate = Path(finetune).resolve(strict=True) if finetune else weights
    if not Path(pretrained).is_absolute() or (finetune and not Path(finetune).is_absolute()):
        raise ValueError("Checkpoint paths must be absolute")
    circuit = ROOT / "models/v2_original.pt"
    for path in {weights, candidate}:
        if path.suffix != ".pt" or (circuit.is_file() and sha256(path) == sha256(circuit)):
            raise ValueError("Use general pretrained/mechanics checkpoints, never circuit weights")
    if not 1 <= epochs <= 500 or imgsz < 32 or imgsz % 32:
        raise ValueError("Invalid epochs/image size")
    leakage = audit(manifest, root)
    if not leakage["passed"]:
        raise ValueError("Dataset leakage audit failed")
    if not smoke and any(n < 20 for n in leakage["frozen_styles"].values()):
        raise ValueError(
            "Freeze 20 printed and 20 handwritten HUMAN gold scenes before full training; --smoke is plumbing only"
        )
    if not all(any(r["split"] == s for r in manifest["records"]) for s in ("train", "val")):
        raise ValueError("Training and validation are required")
    return {
        "domain": "mechanics",
        "dataset": str(root),
        "dataset_manifest_sha256": sha256(root / "manifest.json"),
        "origin": manifest["origin"],
        "out": str(out),
        "device": device,
        "epochs": 1 if smoke else epochs,
        "imgsz": imgsz,
        "seed": seed,
        "smoke_only": smoke,
        "candidates": {"fine_tune": str(candidate), "pretrained_control": str(weights)},
        "checkpoint_sha256": {str(p): sha256(p) for p in {weights, candidate}},
        "leakage": leakage,
        "promotion_eligible": False,
        "note": "R1 initializes both arms from the same general checkpoint unless a prior mechanics checkpoint is supplied. A one-epoch subset proves plumbing only.",
    }


def copy_training_data(plan, out):
    root = Path(plan["dataset"])
    manifest = load_dataset(root)
    dest = out / "dataset"
    dest.mkdir()
    (dest / "images").mkdir()
    (dest / "labels").mkdir()
    selected = []
    for split in ("train", "val"):
        rows = [r for r in manifest["records"] if r["split"] == split]
        if plan["smoke_only"]:
            picked = []
            for a in ARCHETYPES:
                picked.extend(
                    [r for r in rows if r["archetype"] == a][: 2 if split == "train" else 1]
                )
            rows = picked
        for index, row in enumerate(rows):
            row = dict(row)
            source = root / row["image"]
            name = f"{split}_{index:04d}{source.suffix}"
            shutil.copyfile(source, dest / "images" / name)
            label_name = Path(name).stem + ".txt"
            shutil.copyfile(root / row["label"], dest / "labels" / label_name)
            row.update(image=f"images/{name}", label=f"labels/{label_name}")
            selected.append(row)
        (dest / (split + ".txt")).write_text(
            "\n".join("./" + r["image"] for r in selected if r["split"] == split) + "\n",
            encoding="utf-8",
        )
    manifest["records"] = selected
    write_json(dest / "manifest.json", manifest)
    config = dest / "data.yaml"
    config.write_text(
        yaml.safe_dump(
            {"path": str(dest), "train": "train.txt", "val": "val.txt", "names": list(NAMES)}
        ),
        encoding="utf-8",
    )
    return config


def execute(plan):
    out = fresh(plan["out"])
    # Source datasets are immutable: SDK-generated labels.cache also stays in this run.
    data = copy_training_data(plan, out)
    write_json(out / "plan.json", plan)
    reports = {}
    for name, weights in plan["candidates"].items():
        start = time.perf_counter()
        model = local_model(weights, general=True)
        if name == "pretrained_control" and len(model.names) != 80:
            raise ValueError("Control must be a general 80-class pretrained detector")
        # Known local system font avoids the SDK's automatic font-download branch.
        from ultralytics.utils import USER_CONFIG_DIR

        font = Path("C:/Windows/Fonts/arial.ttf")
        if not font.is_file():
            font = ROOT / "frontend/public/fonts/NotoSansBengali.ttf"
        if not (USER_CONFIG_DIR / "Arial.ttf").is_file():
            shutil.copyfile(font, USER_CONFIG_DIR / "Arial.ttf")
        result = model.train(
            data=str(data),
            epochs=plan["epochs"],
            imgsz=plan["imgsz"],
            device=plan["device"],
            seed=plan["seed"],
            pretrained=True,
            project=str(out),
            name=name,
            exist_ok=False,
            workers=0,
            batch=2,
            amp=False,
            plots=False,
            cache=False,
            optimizer="SGD",
            lr0=0.001,
            freeze=0,
            deterministic=True,
            mosaic=0,
            mixup=0,
            cutmix=0,
            copy_paste=0,
            degrees=0,
            translate=0,
            scale=0,
            fliplr=0,
            flipud=0,
            hsv_h=0,
            hsv_s=0,
            hsv_v=0,
        )
        directory = Path(model.trainer.save_dir).resolve()
        if not directory.is_relative_to(out):
            raise RuntimeError("SDK output escaped the run")
        best = directory / "weights/best.pt"
        training_seconds = time.perf_counter() - start
        metrics = evaluate(data.parent, best, imgsz=plan["imgsz"], device=plan["device"])
        metrics["smoke_only"] = plan["smoke_only"]
        metrics["training_seconds"] = training_seconds
        metrics["training_metrics_available"] = result is not None
        write_json(directory / "evaluation.json", metrics)
        (directory / "MODEL_CARD.md").write_text(
            "# Mechanics candidate\n\n"
            + json.dumps(plan, indent=2)
            + "\n\nSynthetic validation is not real accuracy. Smoke candidates cannot be promoted. No full/GPU training is claimed. Ultralytics licensing requires owner review.\n",
            encoding="utf-8",
        )
        reports[name] = {
            "weights": str(best),
            "weights_sha256": sha256(best),
            "training_seconds": training_seconds,
            "evaluation": metrics,
        }
    write_json(out / "summary.json", reports)
    return reports


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", required=True, type=Path)
    p.add_argument("--pretrained", required=True, type=Path)
    p.add_argument("--finetune", type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--device", default="cpu")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--execute", action="store_true")
    a = p.parse_args()
    plan = training_plan(
        a.data,
        a.pretrained,
        a.out,
        finetune=a.finetune,
        smoke=a.smoke,
        device=a.device,
        epochs=a.epochs,
        imgsz=a.imgsz,
        seed=a.seed,
    )
    print(json.dumps(plan, indent=2))
    if a.execute:
        execute(plan)


if __name__ == "__main__":
    main()
