"""M4 contracts and review/leakage tools. All review records here are synthetic TEST mocks."""

import copy
import json
from pathlib import Path
import shutil
from types import SimpleNamespace
import uuid

import numpy as np
from PIL import Image
import pytest

from circuit_sim.backend.domains.mechanics.config import mechanics_config
from circuit_sim.backend.tools.mechanics.build_fixtures import fixtures
from circuit_sim.backend.tools.mechanics.common import (
    ROOT,
    NAMES,
    ARCHETYPES,
    contained,
    fresh,
    load_dataset,
    read_labels,
    sha256,
    write_json,
)
from circuit_sim.backend.tools.mechanics.compare_detectors import promotion
from circuit_sim.backend.tools.mechanics.eval_detector import (
    score,
    evaluate,
    evaluate_frozen,
    quota,
    protocol,
)
from circuit_sim.backend.tools.mechanics.gold import validate_gold, freeze, verify_frozen
from circuit_sim.backend.tools.mechanics.leakage import audit
from circuit_sim.backend.tools.mechanics.make_gold_template import make_template
from circuit_sim.backend.tools.mechanics.prelabel import propose
from circuit_sim.backend.tools.mechanics.import_reviewed import import_export
from circuit_sim.backend.tools.mechanics.train import training_plan, copy_training_data


@pytest.fixture
def work():
    base = (ROOT / ".cache/m4-unit").resolve()
    path = base / uuid.uuid4().hex
    path.mkdir(parents=True)
    yield path
    assert path.resolve().is_relative_to(base) and base.is_relative_to(ROOT)
    shutil.rmtree(path)


def image(path, other=False):
    raster = Image.new("RGB", (800, 520), "white")
    from PIL import ImageDraw

    d = ImageDraw.Draw(raster)
    d.line([(40, 450), (700, 450)], fill="black", width=3)
    if other:
        d.ellipse((400, 80, 500, 180), outline="black", width=4)
    else:
        d.rectangle((100, 200, 160, 240), outline="black", width=4)
    path.parent.mkdir(parents=True, exist_ok=True)
    raster.save(path)


def dataset(root, origin="synthetic"):
    (root / "images").mkdir(parents=True)
    (root / "labels").mkdir()
    rows = []
    for i in range(2):
        p = root / f"images/{i}.png"
        image(p, bool(i))
        label = root / f"labels/{i}.txt"
        label.write_text("0 0.1625 0.423076923 0.075 0.076923077\n")
        rows.append(
            {
                "image": f"images/{i}.png",
                "label": f"labels/{i}.txt",
                "sha256": sha256(p),
                "label_sha256": sha256(label),
                "split": "train" if i == 0 else "val",
                "source_group": f"TEST-SOURCE-{i}",
                "archetype": "incline_block",
                "style": "printed",
                "human_reviewed": origin == "real",
                "reviewer": "TEST MOCK ONLY",
                "source": "synthetic unit test",
                "licence_note": "TEST FIXTURE, not a real licence decision",
            }
        )
    m = {"domain": "mechanics", "origin": origin, "class_names": list(NAMES), "records": rows}
    write_json(root / "manifest.json", m)
    return m


def mock_gold(root):
    # A validator fixture, outside the actual frozen tree. It is not HUMAN gold.
    p = root / "printed/example.gold.json"
    image(p.parent / "images/example.png")
    scene = fixtures()["incline"].model_dump(mode="json", by_alias=True)
    item = {
        "kind": "mechanics-human-gold",
        "version": 1,
        "source": {
            "image": "images/example.png",
            "sha256": sha256(p.parent / "images/example.png"),
            "group": "TEST-SOURCE-0",
            "reference": "SYNTHETIC TEST ONLY",
            "licence_note": "TEST MOCK, not a licence approval",
        },
        "review": {
            "human_reviewed": True,
            "reviewer": "TEST MOCK ONLY",
            "reviewed_at": "2026-11-13",
            "notes": "Not an actual review",
        },
        "scene": scene,
    }
    write_json(p, item)
    return p, item


def test_fixed_class_order_and_mechanics_environment_do_not_change_circuit(monkeypatch):
    assert (
        len(NAMES) == 21
        and NAMES[:4] == ("block", "ball", "bob", "cart")
        and NAMES[-1] == "text_label"
    )
    monkeypatch.setenv("MECHANICS_MODEL", "models/custom-mechanics.pt")
    cfg = mechanics_config()
    assert Path(cfg["weights"]) == ROOT / "models/custom-mechanics.pt"
    from circuit_sim.backend.core import load_config

    assert Path(load_config()["detector"]["weights"]).name == "v2_original.pt"


def test_contained_fresh_outputs_refuse_escape_overwrite_and_gold(work):
    for path in (
        "relative",
        ROOT,
        ROOT.parent / "escape",
        ROOT / "data/eval/mechanics/printed/output",
    ):
        with pytest.raises(ValueError):
            fresh(path)
    dest = fresh(work / "new")
    (dest / "keep.txt").write_text("owner")
    with pytest.raises(ValueError):
        fresh(dest)
    assert (dest / "keep.txt").read_text() == "owner"


@pytest.mark.parametrize(
    "line",
    [
        "0 nan .5 .1 .1",
        "21 .5 .5 .1 .1",
        "1.5 .5 .5 .1 .1",
        "0 0 .5 .2 .1",
        "0 .5 .5 0 .1",
        "0 .5 .5 .1 .1 extra",
    ],
)
def test_yolo_contract_rejects_invalid_class_nonfinite_and_clipping(work, line):
    p = work / "bad.txt"
    p.write_text(line)
    with pytest.raises(ValueError):
        read_labels(p, 800, 520)


def test_null_gold_scaffold_cannot_be_validated_as_reviewed_gold(work):
    src = work / "image.png"
    image(src)
    scaffold = make_template(src, work / "scaffold")
    assert scaffold["scene"] is None and scaffold["review"]["human_reviewed"] is False
    with pytest.raises(ValueError, match="HUMAN"):
        validate_gold(work / "scaffold/human-template.json")


def test_gold_hashes_are_immutable_and_portable_and_no_scene_is_written(work):
    root = work / "TEST-frozen"
    p, _ = mock_gold(root)
    before = p.read_bytes()
    result = freeze(root, root / "frozen.json")
    assert result["minimum_20_each_met"] is False
    assert p.read_bytes() == before and not Path(result["records"][0]["image"]).is_absolute()
    assert len(verify_frozen(root)) == 1
    with pytest.raises(FileExistsError):
        freeze(root, root / "frozen.json")
    with p.open("a") as file:
        file.write(" ")
    with pytest.raises(ValueError, match="changed"):
        verify_frozen(root)


@pytest.mark.parametrize("field", ["human", "hash", "ref", "unit", "image_size"])
def test_gold_validator_rejects_incomplete_or_changed_mock_review(work, field):
    p, item = mock_gold(work / "TEST-frozen")
    if field == "human":
        item["review"]["human_reviewed"] = False
    if field == "hash":
        item["source"]["sha256"] = "0" * 64
    if field == "ref":
        item["scene"]["links"].append(
            {
                "id": "bad",
                "type": "rope",
                "a": {"ref": "missing", "point": [1, 2]},
                "b": {"ref": "B1", "point": [2, 3]},
                "polyline": [[1, 2], [2, 3]],
            }
        )
    if field == "unit":
        item["scene"]["bodies"][0]["mass"]["unit"] = "g"
    if field == "image_size":
        item["scene"]["image"]["width"] = 799
    write_json(p, item)
    with pytest.raises(ValueError):
        validate_gold(p)


def test_leakage_catches_exact_near_and_source_group_crossings(work):
    root = work / "dataset"
    m = dataset(root)
    empty = work / "empty-frozen"
    assert audit(m, root, empty)["passed"]
    m["records"][1]["source_group"] = m["records"][0]["source_group"]
    assert not audit(m, root, empty)["passed"]
    m["records"][1]["source_group"] = "OTHER"
    shutil.copyfile(root / "images/0.png", root / "images/1.png")
    result = audit(m, root, empty)
    assert any(c["kind"] == "near_duplicate_split" and c["exact"] for c in result["collisions"])
    with Image.open(root / "images/0.png") as im:
        im.resize((600, 390)).save(root / "images/1.png")
    assert any(
        c["kind"] == "near_duplicate_split" and not c["exact"]
        for c in audit(m, root, empty)["collisions"]
    )
    frozen = work / "TEST-frozen"
    mock_gold(frozen)
    freeze(frozen, frozen / "frozen.json")
    assert any(c["kind"] == "frozen_overlap" for c in audit(m, root, frozen)["collisions"])


def test_dataset_integrity_checks_content_labels_and_origin(work):
    root = work / "data"
    m = dataset(root)
    load_dataset(root)
    (root / "labels/0.txt").write_text("")
    with pytest.raises(ValueError, match="Label hash"):
        load_dataset(root)
    m["origin"] = "unreviewed"
    write_json(root / "manifest.json", m)
    with pytest.raises(ValueError, match="origin"):
        load_dataset(root)


def test_evaluator_known_ap_duplicates_wrong_classes_and_empty_support():
    gt = {"a": [(0, [0, 0, 10, 10])], "b": [(1, [0, 0, 10, 10])]}
    pred = {
        "a": [(0, 0.99, [0, 0, 10, 10]), (0, 0.8, [0, 0, 10, 10])],
        "b": [(0, 0.9, [0, 0, 10, 10])],
    }
    metrics = score(gt, pred)
    assert metrics["block"]["recall"] == 1
    assert metrics["block"]["precision"] == pytest.approx(1 / 3)
    assert metrics["block"]["AP50"] == 1
    assert metrics["ball"]["recall"] == 0 and metrics["ball"]["AP50"] == 0
    assert metrics["bob"]["recall"] is None and metrics["bob"]["AP50"] is None
    fp_first = score(
        {"a": [(0, [0, 0, 10, 10])]}, {"a": [(0, 0.99, [40, 40, 50, 50]), (0, 0.9, [0, 0, 10, 10])]}
    )
    assert fp_first["block"]["AP50_95"] == 0.5


class Stub:
    def predict(self, *args, **kwargs):
        return [
            SimpleNamespace(
                boxes=[
                    SimpleNamespace(
                        cls=np.array([0]),
                        conf=np.array([0.9]),
                        xyxy=np.array([[100, 200, 160, 240]]),
                    )
                ]
            )
        ]


def test_evaluation_and_real_quotas_use_provenance_and_explicit_protocol(work):
    root = work / "dataset"
    dataset(root)
    weights = work / "STUB.pt"
    weights.write_bytes(b"TEST ONLY")
    metrics = evaluate(root, weights, model=Stub(), imgsz=192)
    assert metrics["origin"] == "synthetic" and "not real accuracy" in metrics["label"]
    assert metrics["classes"]["block"]["recall"] == 1 and metrics["protocol"]["imgsz"] == 192
    with pytest.raises(ValueError):
        quota(root)
    real = work / "mock-review"
    dataset(real, origin="real")
    q = quota(real)
    assert (
        q["images"] == 2
        and q["classes"]["block"]["instances"] == 2
        and q["classes"]["block"]["minimum_deficit"] == 23
    )
    assert quota(work / "empty")["images"] == 0
    null = evaluate_frozen(work / "no-gold", None)
    assert null["classes"]["block"]["AP50"] is None and null["seconds"] is None


def test_prelabels_are_unreviewed_and_review_import_requires_exact_attestation(work):
    src = work / "source"
    src.mkdir()
    image(src / "one.png")
    weights = work / "STUB.pt"
    weights.write_bytes(b"TEST ONLY")
    proposals = work / "proposals"
    p = propose(src, weights, proposals, model=Stub())
    assert p["origin"] == "unreviewed" and p["records"][0]["human_reviewed"] is False
    with pytest.raises(ValueError):
        load_dataset(proposals)
    row = p["records"][0]
    review = {
        "kind": "mechanics-human-review",
        "version": 1,
        "class_names": list(NAMES),
        "records": [
            {
                **row,
                "reviewed_label_sha256": row["label_sha256"],
                "human_reviewed": True,
                "reviewer": "SYNTHETIC TEST MOCK",
                "reviewed_at": "2026-11-13",
                "source": "TEST FIXTURE",
                "source_group": "TEST-group",
                "licence_note": "MOCK ONLY",
                "archetype": "incline_block",
                "style": "printed",
                "split": "train",
            }
        ],
    }
    review_file = work / "review.json"
    write_json(review_file, review)
    result = import_export(proposals, review_file, work / "imported", frozen_root=work / "empty")
    assert result["origin"] == "real" and result["records"][0]["review_manifest_sha256"] == sha256(
        review_file
    )
    load_dataset(work / "imported")
    review["records"][0]["human_reviewed"] = False
    write_json(review_file, review)
    with pytest.raises(ValueError, match="HUMAN"):
        import_export(proposals, review_file, work / "refused")


def test_training_plan_is_safe_smoke_and_cannot_use_circuit_weights(work):
    root = work / "dataset"
    dataset(root)
    checkpoint = work / "STUB.pt"
    checkpoint.write_bytes(b"TEST ONLY")
    plan = training_plan(root, checkpoint, work / "run", smoke=True, imgsz=192)
    assert plan["epochs"] == 1 and not plan["promotion_eligible"] and not (work / "run").exists()
    with pytest.raises(ValueError, match="20 printed"):
        training_plan(root, checkpoint, work / "full-run", smoke=False)
    out = fresh(work / "run")
    data = copy_training_data(plan, out)
    load_dataset(data.parent)
    for invalid in ("relative", ROOT.parent / "escape", root / "output"):
        with pytest.raises(ValueError):
            training_plan(root, checkpoint, invalid)
    circuit = ROOT / "models/v2_original.pt"
    if circuit.is_file():
        with pytest.raises(ValueError, match="circuit"):
            training_plan(root, circuit, work / "wrong")


def test_external_class_mapping_binds_reviewed_labels_and_refuses_frozen_sources(work):
    export = work / "external"
    image(export / "images/one.png")
    label = export / "labels/one.txt"
    label.parent.mkdir()
    label.write_text("0 0.5 0.5 0.1 0.1\n1 0.2 0.2 0.1 0.1\n")
    review = {
        "kind": "mechanics-human-review",
        "version": 1,
        "class_names": ["ExternalBox", "ExternalDecoration"],
        "records": [
            {
                "image": "images/one.png",
                "label": "labels/one.txt",
                "sha256": sha256(export / "images/one.png"),
                "reviewed_label_sha256": sha256(label),
                "human_reviewed": True,
                "reviewer": "SYNTHETIC TEST MOCK",
                "reviewed_at": "2026-11-13",
                "source": "SYNTHETIC TEST FIXTURE",
                "source_group": "TEST-external",
                "licence_note": "MOCK ONLY",
                "archetype": "incline_block",
                "style": "printed",
                "split": "train",
            }
        ],
    }
    review_file = work / "external-review.json"
    write_json(review_file, review)
    with pytest.raises(ValueError, match="Map every source"):
        import_export(export, review_file, work / "unmapped")
    mapping = {"ExternalBox": "block", "ExternalDecoration": None}
    result = import_export(
        export, review_file, work / "mapped", class_map=mapping, frozen_root=work / "empty"
    )
    assert result["source_class_map"] == mapping
    assert result["records"][0]["dropped_unmapped_classes"] == 1
    assert len(read_labels(work / "mapped/labels/real_0000.txt", 800, 520)) == 1
    before = label.read_bytes()
    label.write_text("0 0.6 0.5 0.1 0.1\n")
    with pytest.raises(ValueError, match="hash mismatch"):
        import_export(export, review_file, work / "tampered", class_map=mapping)
    label.write_bytes(before)
    frozen = work / "TEST-frozen"
    mock_gold(frozen)
    freeze(frozen, frozen / "frozen.json")
    with pytest.raises(ValueError, match="leakage"):
        import_export(
            export, review_file, work / "frozen-rejected", class_map=mapping, frozen_root=frozen
        )
    assert not (work / "frozen-rejected/manifest.json").exists()
    assert (work / "frozen-rejected/REJECTED.json").is_file()


def test_promotion_rejects_smoke_wrong_protocol_and_common_regression():
    base = {
        "origin": "real",
        "frozen_real": True,
        "smoke_only": False,
        "style": "printed",
        "images": 20,
        "image_sha256": ["TEST"],
        "protocol": protocol(),
        "classes": {n: {"support": 30, "recall": 0.8} for n in NAMES},
    }
    new = copy.deepcopy(base)
    new["classes"]["spring"]["recall"] = 0.9
    assert promotion(base, new, ["spring"])["eligible"]
    for field, value in [
        ("smoke_only", True),
        ("origin", "synthetic"),
        ("protocol", protocol(192)),
    ]:
        bad = copy.deepcopy(new)
        bad[field] = value
        assert not promotion(base, bad, ["spring"])["eligible"]
    new["classes"]["block"]["recall"] = 0.77
    assert not promotion(base, new, ["spring"])["eligible"]
