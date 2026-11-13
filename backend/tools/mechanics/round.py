"""Repeatable mechanics review/fine-tune/evaluation rounds; never auto-approve labels or install models."""

import argparse
from collections import Counter, defaultdict
import json
import math
from pathlib import Path
import random
import shlex
import shutil
import subprocess
import sys
import uuid

import yaml

from ...core import signature, near
from .common import ROOT, FROZEN, NAMES, contained, fresh, images, load_dataset, sha256, write_json
from .compare_detectors import promotion
from .eval_detector import evaluate_frozen, protocol, quota
from .gold import verify_frozen
from .import_reviewed import import_export
from .leakage import audit
from .prelabel import propose


def read_round(run):
    run = contained(run)
    state = json.loads((run / "round.json").read_text(encoding="utf-8"))
    if state.get("kind") != "mechanics-round" or state.get("version") != 1:
        raise ValueError("Not a mechanics round")
    if contained(state["run"]) != run:
        raise ValueError("Round directory changed; start a new round")
    return state


def persist(state):
    run = contained(state["run"])
    report = contained(ROOT / f"docs/mechanics/rounds/round-{state['number']}.md")
    marker = f"<!-- mechanics-round {state['id']} -->"
    if report.exists() and marker not in report.read_text(encoding="utf-8"):
        raise ValueError("Refusing to replace another round report")
    report.parent.mkdir(parents=True, exist_ok=True)
    write_json(run / "round.json", state)
    lines = [
        f"# Mechanics round {state['number']}",
        "",
        marker,
        "",
        "Real evaluation and human review are required; this tool never installs a candidate.",
        "",
        f"Protocol: image size {state['protocol']['imgsz']}, confidence {state['protocol']['confidence']}, matching IoU 0.50.",
        f"Declared target classes: {', '.join(state['targets'])}.",
        "",
        f"Pre-label stage: {'completed, proposals UNREVIEWED' if state.get('proposals') else 'null — HUMAN: supply a source-separated real pool and a local detector.'}",
        f"Merge stage: {'completed from HUMAN-attested imports' if state.get('merge') else 'null — HUMAN: review every label and provide its immutable export/review manifest.'}",
        "",
    ]
    if state.get("merge"):
        lines += [
            f"Exposure cap: at most {state['merge']['max_synthetic_per_real']} synthetic images per real image in each split; {state['merge']['counts']}.",
            "",
        ]
    if state.get("training_command"):
        lines += [
            "Fine-tune command (printed only, not executed by this round):",
            "",
            "```",
            state["training_command"],
            "```",
            "",
        ]
    decisions = state.get("promotion", {})
    for style in ("printed", "handwritten"):
        measured = state.get("evaluation", {}).get(style, {})
        old, new = measured.get("baseline", {}), measured.get("candidate", {})
        lines += [
            f"## Real {style}",
            "",
            f"Images: {new.get('images', 0)}. Promotion eligible: {decisions.get(style, {}).get('eligible', False)}.",
            "",
            "| Class | Old recall | New recall | New precision | New AP50 | New AP50:95 |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]

        def metric(report, name, key):
            value = report.get("classes", {}).get(name, {}).get(key)
            return "null" if value is None else f"{value:.6f}"

        for name in NAMES:
            lines.append(
                f"| {name} | {metric(old, name, 'recall')} | {metric(new, name, 'recall')} | {metric(new, name, 'precision')} | {metric(new, name, 'AP50')} | {metric(new, name, 'AP50_95')} |"
            )
        lines += ["", *[f"- {r}" for r in decisions.get(style, {}).get("reasons", [])], ""]
    lines += [
        f"Overall promotion eligible: **{state.get('promotion_eligible', False)}**.",
        "",
        "HUMAN: independently author/review frozen real scenes/labels, annotate disjoint training data, decide licences, run adequate retraining and review Bangla/devices. Missing metrics are null; synthetic scores cannot satisfy promotion.",
        "",
    ]
    report.write_text("\n".join(lines), encoding="utf-8")


def initialize(run, number, targets, *, imgsz=640, confidence=0.25):
    if type(number) is not int or not 1 <= number <= 9999:
        raise ValueError("Round number must be 1..9999")
    if not targets or len(set(targets)) != len(targets) or any(t not in NAMES for t in targets):
        raise ValueError("Declare unique supported target classes before evaluation")
    report = contained(ROOT / f"docs/mechanics/rounds/round-{number}.md")
    if report.exists():
        raise ValueError("Round report already exists; use a new number")
    out = fresh(run)
    state = dict(
        kind="mechanics-round",
        version=1,
        id=uuid.uuid4().hex,
        run=str(out),
        number=number,
        targets=list(targets),
        protocol=protocol(imgsz, confidence),
        promotion_eligible=False,
    )
    persist(state)
    return state


def prelabel_round(run, pool, weights, *, device="cpu"):
    state = read_round(run)
    if state.get("proposals") or state.get("evaluation"):
        raise ValueError("Pre-label once before evaluation; use a new round for new targets/data")
    frozen = [(r, signature(r["image"])) for r in verify_frozen(FROZEN)]
    for path in images(pool):
        sig = signature(path)
        if any(near(sig, frozen_sig) for _, frozen_sig in frozen):
            raise ValueError("Frozen image/near-duplicate cannot enter the real pool")
    weights = Path(weights).resolve(strict=True)
    result = propose(
        pool,
        weights,
        Path(state["run"]) / "proposals",
        imgsz=state["protocol"]["imgsz"],
        confidence=state["protocol"]["confidence"],
        device=device,
    )
    state["baseline"] = dict(path=str(weights), sha256=sha256(weights))
    state["proposals"] = dict(
        images=len(result["records"]),
        human_reviewed=False,
        manifest_sha256=sha256(Path(state["run"]) / "proposals/manifest.json"),
    )
    persist(state)
    return state


def merge_datasets(
    real_root, synthetic_root, output, *, max_synthetic_per_real=2.0, seed=42, frozen_root=FROZEN
):
    if not math.isfinite(max_synthetic_per_real) or max_synthetic_per_real < 0:
        raise ValueError("Exposure cap must be finite and nonnegative")
    real_root, synthetic_root = Path(real_root).resolve(), Path(synthetic_root).resolve()
    real, synthetic = load_dataset(real_root), load_dataset(synthetic_root)
    if (
        real["origin"] != "real"
        or synthetic["origin"] != "synthetic"
        or any(r.get("synthetic") is not True for r in synthetic["records"])
    ):
        raise ValueError("Merge requires reviewed real data and explicitly synthetic images")
    out = contained(output)
    if any(out == p or out.is_relative_to(p) for p in (real_root, synthetic_root)):
        raise ValueError("Merge output must not be inside an input dataset")
    chosen = []
    rng = random.Random(seed)
    counts = {}
    for split in ("train", "val"):
        real_rows = [r for r in real["records"] if r["split"] == split]
        if not real_rows:
            raise ValueError("Reviewed real examples are required in both train and val")
        chosen.extend((real_root, r, False) for r in real_rows)
        budget = math.floor(len(real_rows) * max_synthetic_per_real)
        groups = defaultdict(list)
        for row in synthetic["records"]:
            if row["split"] == split:
                groups[row["source_group"]].append(row)
        group_names = sorted(groups)
        rng.shuffle(group_names)
        selected = []
        for group in group_names:
            if len(selected) + len(groups[group]) <= budget:
                selected.extend(groups[group])
        chosen.extend((synthetic_root, r, True) for r in selected)
        counts[split] = dict(real=len(real_rows), synthetic=len(selected), cap=budget)
    out = fresh(out)
    for name in ("images", "labels"):
        (out / name).mkdir()
    records = []
    for i, (source, row, is_synthetic) in enumerate(chosen):
        stem = f"{'synthetic' if is_synthetic else 'real'}_{i:05d}"
        image = f"images/{stem}{Path(row['image']).suffix}"
        label = f"labels/{stem}.txt"
        shutil.copyfile(source / row["image"], out / image)
        shutil.copyfile(source / row["label"], out / label)
        records.append(
            {
                **row,
                "image": image,
                "label": label,
                "synthetic": is_synthetic,
                "input_manifest_sha256": sha256(source / "manifest.json"),
                "input_image": row["image"],
                "input_label": row["label"],
            }
        )
    manifest = dict(
        version=1,
        domain="mechanics",
        origin="mixed",
        class_names=list(NAMES),
        records=records,
        exposure_cap=dict(max_synthetic_per_real=max_synthetic_per_real, counts=counts, seed=seed),
        benchmark_note="Mixed training/validation, never frozen real accuracy",
    )
    leakage = audit(manifest, out, frozen_root)
    write_json(out / "leakage.json", leakage)
    if not leakage["passed"]:
        write_json(
            out / "REJECTED.json", dict(reason="Merge failed frozen/source/duplicate leakage audit")
        )
        raise ValueError("Merged dataset failed leakage audit")
    write_json(out / "manifest.json", manifest)
    for split in ("train", "val"):
        (out / (split + ".txt")).write_text(
            "\n".join("./" + r["image"] for r in records if r["split"] == split) + "\n",
            encoding="utf-8",
        )
    (out / "data.yaml").write_text(
        yaml.safe_dump(dict(path=str(out), train="train.txt", val="val.txt", names=list(NAMES))),
        encoding="utf-8",
    )
    load_dataset(out)
    return manifest


def import_and_merge(
    run,
    export,
    review,
    synthetic,
    baseline,
    pretrained,
    *,
    ratio=2.0,
    seed=42,
    device="0",
    epochs=50,
):
    state = read_round(run)
    if state.get("merge") or state.get("evaluation"):
        raise ValueError("Merge once before evaluation")
    base = Path(baseline).resolve(strict=True)
    general = Path(pretrained).resolve(strict=True)
    bound = state.get("baseline")
    if bound and bound["sha256"] != sha256(base):
        raise ValueError("Baseline differs from this round's pre-label model")
    run = Path(state["run"])
    imported = run / "reviewed"
    import_export(export, review, imported)
    merged = merge_datasets(
        imported, synthetic, run / "merged", max_synthetic_per_real=ratio, seed=seed
    )
    state["baseline"] = dict(path=str(base), sha256=sha256(base))
    state["merge"] = merged["exposure_cap"]
    state["real_quota"] = quota(imported)
    command = [
        sys.executable,
        "-m",
        "backend.tools.mechanics.train",
        "--data",
        str(run / "merged"),
        "--pretrained",
        str(general),
        "--finetune",
        str(base),
        "--out",
        str(run / "training"),
        "--imgsz",
        str(state["protocol"]["imgsz"]),
        "--epochs",
        str(epochs),
        "--device",
        device,
        "--execute",
    ]
    state["training_command_args"] = command
    state["training_command"] = (
        subprocess.list2cmdline(command) if sys.platform == "win32" else shlex.join(command)
    )
    persist(state)
    print(state["training_command"])
    return state


def unmeasured(style, settings, records, reason):
    rows = [r for r in records if r["style"] == style]
    return dict(
        domain="mechanics",
        origin="real",
        style=style,
        split="frozen",
        frozen_real=bool(rows),
        smoke_only=False,
        images=len(rows),
        image_sha256=sorted(r["sha256"] for r in rows),
        protocol=settings,
        seconds=None,
        human_task=reason,
        classes={
            n: dict.fromkeys(("support", "precision", "recall", "AP50", "AP50_95")) for n in NAMES
        },
    )


def evaluate_round(
    run,
    candidate=None,
    *,
    baseline=None,
    frozen_root=FROZEN,
    device="cpu",
    evaluator=evaluate_frozen,
):
    state = read_round(run)
    if state.get("evaluation"):
        raise ValueError("Evaluation is immutable; use a new round")
    baseline = baseline or state.get("baseline", {}).get("path")
    weights = {}
    for name, path in (("baseline", baseline), ("candidate", candidate)):
        if path:
            path = Path(path).resolve(strict=True)
            weights[name] = dict(path=str(path), sha256=sha256(path))
    if (
        state.get("baseline")
        and weights.get("baseline", {}).get("sha256") != state["baseline"]["sha256"]
    ):
        raise ValueError("Baseline checkpoint changed")
    frozen_root = Path(frozen_root).resolve()
    frozen = verify_frozen(frozen_root)
    freeze_file = frozen_root / "frozen.json"
    freeze_hash = sha256(freeze_file) if freeze_file.is_file() else None
    evaluation, decisions = {}, {}
    for style in ("printed", "handwritten"):
        evaluation[style] = {}
        for name in ("baseline", "candidate"):
            if name not in weights:
                result = unmeasured(
                    style,
                    state["protocol"],
                    frozen,
                    "HUMAN: supply local checkpoints and independently reviewed frozen labels/scenes",
                )
            else:
                result = evaluator(
                    frozen_root,
                    weights[name]["path"],
                    style=style,
                    imgsz=state["protocol"]["imgsz"],
                    confidence=state["protocol"]["confidence"],
                    device=device,
                )
            evaluation[style][name] = result
        decisions[style] = promotion(
            evaluation[style]["baseline"], evaluation[style]["candidate"], state["targets"]
        )
    verify_frozen(frozen_root)
    if (sha256(freeze_file) if freeze_file.is_file() else None) != freeze_hash:
        raise ValueError("Frozen inventory changed during comparison")
    state.update(
        evaluation=evaluation,
        promotion=decisions,
        compared_weights=weights,
        promotion_eligible=all(r["eligible"] for r in decisions.values()),
    )
    persist(state)
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="phase", required=True)
    init = sub.add_parser("init")
    init.add_argument("--out", type=Path, required=True)
    init.add_argument("--number", type=int, required=True)
    init.add_argument("--targets", nargs="+", required=True)
    init.add_argument("--imgsz", type=int, default=640)
    init.add_argument("--confidence", type=float, default=0.25)
    pre = sub.add_parser("prelabel")
    pre.add_argument("--run", type=Path, required=True)
    pre.add_argument("--pool", type=Path, required=True)
    pre.add_argument("--weights", type=Path, required=True)
    pre.add_argument("--device", default="cpu")
    merge = sub.add_parser("merge")
    for name in ("run", "export", "review", "synthetic", "baseline", "pretrained"):
        merge.add_argument("--" + name, type=Path, required=True)
    merge.add_argument("--ratio", type=float, default=2.0)
    merge.add_argument("--seed", type=int, default=42)
    merge.add_argument("--epochs", type=int, default=50)
    merge.add_argument("--device", default="0")
    evaluate = sub.add_parser("evaluate")
    evaluate.add_argument("--run", type=Path, required=True)
    evaluate.add_argument("--candidate", type=Path)
    evaluate.add_argument("--baseline", type=Path)
    evaluate.add_argument("--device", default="cpu")
    args = parser.parse_args()
    if args.phase == "init":
        state = initialize(
            args.out, args.number, args.targets, imgsz=args.imgsz, confidence=args.confidence
        )
    elif args.phase == "prelabel":
        state = prelabel_round(args.run, args.pool, args.weights, device=args.device)
    elif args.phase == "merge":
        state = import_and_merge(
            args.run,
            args.export,
            args.review,
            args.synthetic,
            args.baseline,
            args.pretrained,
            ratio=args.ratio,
            seed=args.seed,
            device=args.device,
            epochs=args.epochs,
        )
    else:
        state = evaluate_round(args.run, args.candidate, baseline=args.baseline, device=args.device)
    print(json.dumps({k: state[k] for k in ("number", "run", "promotion_eligible")}))


if __name__ == "__main__":
    main()
