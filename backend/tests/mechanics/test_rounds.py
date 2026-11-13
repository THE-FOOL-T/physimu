"""Round TEST mocks, never real labels, real gold, licence approval or accuracy."""

import copy
from datetime import date
import json
from pathlib import Path
import random
import shutil
import uuid

import numpy as np
from PIL import Image, ImageDraw
import pytest

from circuit_sim.backend.tools.mechanics import round as rounds
from circuit_sim.backend.tools.mechanics.common import ROOT, NAMES, load_dataset, sha256, write_json
from circuit_sim.backend.tools.mechanics.train import training_plan


@pytest.fixture
def work(monkeypatch):
    base = ROOT / ".cache/m6-round-tests"
    path = base / uuid.uuid4().hex
    path.mkdir(parents=True)
    monkeypatch.setattr(rounds, "ROOT", path)
    yield path
    assert path.resolve().is_relative_to(base.resolve())
    shutil.rmtree(path)


def data(root, count, *, real=False, offset=0):
    (root / "images").mkdir(parents=True)
    (root / "labels").mkdir()
    records = []
    for i in range(count):
        rng = random.Random(offset + i)
        raster = Image.new("RGB", (180, 120), "white")
        draw = ImageDraw.Draw(raster)
        for _ in range(18):
            draw.line(
                [
                    (rng.randrange(180), rng.randrange(120)),
                    (rng.randrange(180), rng.randrange(120)),
                ],
                fill="black",
                width=2,
            )
        image = root / f"images/{i}.png"
        label = root / f"labels/{i}.txt"
        raster.save(image)
        label.write_text("0 0.5 0.5 0.3 0.3\n", encoding="utf-8")
        records.append(
            dict(
                image=f"images/{i}.png",
                label=f"labels/{i}.txt",
                sha256=sha256(image),
                label_sha256=sha256(label),
                split="train" if i < count // 2 else "val",
                source_group=f"TEST-{offset + i}",
                archetype="incline_block",
                style="printed",
                synthetic=not real,
                human_reviewed=real,
                reviewer="TEST MOCK ONLY",
                source="TEST generated mock, not real data",
                licence_note="TEST fixture, not a licence decision",
                reviewed_at=date.today().isoformat(),
            )
        )
    manifest = dict(
        version=1,
        domain="mechanics",
        origin="real" if real else "synthetic",
        class_names=list(NAMES),
        records=records,
    )
    write_json(root / "manifest.json", manifest)
    return manifest


def test_merge_caps_each_split_retains_hashes_reviews_and_source_groups(work):
    real = data(work / "real", 4, real=True)
    synthetic = data(work / "synthetic", 12, offset=100)
    # The selected source groups must stay whole even at a tight exposure cap.
    for i, row in enumerate(synthetic["records"]):
        row["source_group"] = f"TEST-synthetic-{i // 2}"
    write_json(work / "synthetic/manifest.json", synthetic)
    manifest = rounds.merge_datasets(
        work / "real",
        work / "synthetic",
        work / "merged",
        max_synthetic_per_real=1.5,
        frozen_root=work / "empty",
    )
    checked = load_dataset(work / "merged")
    assert checked == manifest and manifest["origin"] == "mixed"
    for split in ("train", "val"):
        rows = [r for r in manifest["records"] if r["split"] == split]
        real_rows = [r for r in rows if not r["synthetic"]]
        generated = [r for r in rows if r["synthetic"]]
        assert len(real_rows) == 2 and len(generated) <= 3
        assert all(r["human_reviewed"] and r["reviewer"] == "TEST MOCK ONLY" for r in real_rows)
        assert all(
            sum(r["source_group"] == s["source_group"] for r in generated) == 2 for s in generated
        )
    assert {r["sha256"] for r in manifest["records"] if not r["synthetic"]} == {
        r["sha256"] for r in real["records"]
    }
    assert all(
        r["input_manifest_sha256"] and r["input_image"] and r["input_label"]
        for r in manifest["records"]
    )
    tampered = copy.deepcopy(manifest)
    tampered["exposure_cap"]["max_synthetic_per_real"] = 0
    write_json(work / "merged/manifest.json", tampered)
    with pytest.raises(ValueError, match="exposure cap"):
        load_dataset(work / "merged")
    write_json(work / "merged/manifest.json", manifest)
    repeat = rounds.merge_datasets(
        work / "real",
        work / "synthetic",
        work / "repeat",
        max_synthetic_per_real=1.5,
        frozen_root=work / "empty",
    )
    assert repeat["records"] == manifest["records"]
    checked["records"][0]["human_reviewed"] = False
    write_json(work / "merged/manifest.json", checked)
    with pytest.raises(ValueError, match="human review"):
        load_dataset(work / "merged")


def test_merge_refuses_unreviewed_duplicate_and_bad_ratios(work):
    data(work / "real", 2, real=True)
    data(work / "synthetic", 2, offset=100)
    for value in (-1, float("nan"), float("inf")):
        with pytest.raises(ValueError, match="cap"):
            rounds.merge_datasets(
                work / "real", work / "synthetic", work / "bad", max_synthetic_per_real=value
            )
    manifest = load_dataset(work / "synthetic")
    shutil.copyfile(work / "real/images/0.png", work / "synthetic/images/1.png")
    manifest["records"][1]["sha256"] = sha256(work / "synthetic/images/1.png")
    write_json(work / "synthetic/manifest.json", manifest)
    with pytest.raises(ValueError, match="leakage"):
        rounds.merge_datasets(
            work / "real",
            work / "synthetic",
            work / "leaked",
            max_synthetic_per_real=2,
            frozen_root=work / "empty",
        )
    assert not (work / "leaked/manifest.json").exists()
    assert (work / "leaked/REJECTED.json").is_file()


def test_review_import_prints_command_without_training_and_retains_gold_gate(work):
    real = data(work / "export", 4, real=True)
    review = dict(kind="mechanics-human-review", version=1, class_names=list(NAMES), records=[])
    for row in real["records"]:
        review["records"].append({**row, "reviewed_label_sha256": row["label_sha256"]})
    write_json(work / "review.json", review)
    data(work / "synthetic", 4, offset=100)
    for name in ("old.pt", "general.pt"):
        (work / name).write_bytes(b"TEST CHECKPOINT ONLY")
    rounds.initialize(work / "run", 1, ["spring", "rope"])
    state = rounds.import_and_merge(
        work / "run",
        work / "export",
        work / "review.json",
        work / "synthetic",
        work / "old.pt",
        work / "general.pt",
        ratio=1,
    )
    assert not (work / "run/training").exists()
    assert "--finetune" in state["training_command_args"]
    assert "--execute" in state["training_command_args"]
    assert not state["promotion_eligible"]
    with pytest.raises(ValueError, match="20 printed"):
        training_plan(
            work / "run/merged",
            work / "general.pt",
            work / "run/training",
            finetune=work / "old.pt",
        )


def test_empty_real_round_records_null_metrics_and_cannot_promote(work):
    rounds.initialize(work / "run", 1, ["spring"])
    state = rounds.evaluate_round(work / "run", frozen_root=work / "empty")
    assert not state["promotion_eligible"]
    for style in ("printed", "handwritten"):
        assert state["evaluation"][style]["candidate"]["classes"]["spring"]["recall"] is None
        assert not state["promotion"][style]["eligible"]
    report = (work / "docs/mechanics/rounds/round-1.md").read_text(encoding="utf-8")
    assert "null" in report and "HUMAN" in report
    with pytest.raises(ValueError, match="immutable"):
        rounds.evaluate_round(work / "run", frozen_root=work / "empty")
    with pytest.raises(ValueError, match="already exists"):
        rounds.initialize(work / "another", 1, ["spring"])


@pytest.mark.parametrize("regression", [False, True])
def test_promotion_requires_both_styles_and_refuses_common_class_regression(work, regression):
    rounds.initialize(work / "run", 1, ["spring"], imgsz=960)
    for name in ("old.pt", "new.pt"):
        (work / name).write_bytes(name.encode())
    calls = []

    def evaluate(root, weights, **options):
        calls.append(options)
        new = Path(weights).name == "new.pt"
        classes = {
            n: dict(support=30, precision=0.5, recall=0.5, AP50=0.4, AP50_95=0.3) for n in NAMES
        }
        classes["spring"]["recall"] = 0.6 if new else 0.5
        if new and regression and options["style"] == "handwritten":
            classes["block"]["recall"] = 0.479
        return dict(
            origin="real",
            frozen_real=True,
            smoke_only=False,
            images=20,
            image_sha256=["TEST FIXTURE ONLY"] * 20,
            style=options["style"],
            protocol=rounds.protocol(options["imgsz"], options["confidence"]),
            classes=classes,
        )

    state = rounds.evaluate_round(
        work / "run",
        work / "new.pt",
        baseline=work / "old.pt",
        frozen_root=work / "empty",
        evaluator=evaluate,
    )
    assert state["promotion_eligible"] is not regression
    assert len(calls) == 4 and all(c["imgsz"] == 960 and c["confidence"] == 0.25 for c in calls)
    if regression:
        assert any(
            "two points" in reason for reason in state["promotion"]["handwritten"]["reasons"]
        )


def test_prelabel_refuses_frozen_content_even_outside_frozen_directory(work, monkeypatch):
    data(work / "pool", 2, offset=100)
    image = work / "pool/images/0.png"
    monkeypatch.setattr(rounds, "verify_frozen", lambda root: [dict(image=image)])
    rounds.initialize(work / "run", 1, ["spring"])
    with pytest.raises(ValueError, match="Frozen image"):
        rounds.prelabel_round(work / "run", work / "pool/images", work / "nonexistent.pt")
