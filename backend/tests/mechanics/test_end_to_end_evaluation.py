"""Metric contracts on synthetic TEST documents; no human gold is authored."""

import copy
import importlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from circuit_sim.backend.tools.mechanics.build_fixtures import fixtures
from circuit_sim.backend.tools.mechanics.eval_end_to_end import (
    evaluate,
    compare_scenes,
    trajectories,
    read_gold_scene,
)


def test_empty_frozen_partitions_are_null_without_loading_any_model(tmp_path):
    def forbidden(*args, **kwargs):
        pytest.fail("An empty frozen set must not execute inference")

    report = evaluate(tmp_path, analyzer=forbidden)
    for partition in report["partitions"].values():
        assert partition["images"] == 0 and partition["human_task"]
        assert all(
            value is None for key, value in partition["metrics"].items() if key != "object_recall"
        )
        assert all(value is None for value in partition["metrics"]["object_recall"].values())


def test_scene_metrics_do_not_credit_assumptions_or_missed_attachments(tmp_path):
    gold = fixtures()["pendulum"].model_dump(mode="json", by_alias=True)
    prediction = copy.deepcopy(gold)
    result = compare_scenes(prediction, gold)
    assert all(result["attachments"])
    assert next(p for p in result["parameters"] if p["path"].endswith(".mass"))["correct"]
    assert not next(p for p in result["parameters"] if p["path"] == "constants.g")[
        "correct"
    ]  # declared prior, even if numerically equal
    prediction["bodies"][0]["mass"]["status"] = "assumed"
    prediction["links"][0]["b"]["ref"] = "pivot"
    result = compare_scenes(prediction, gold)
    assert not all(result["attachments"])
    assert not next(p for p in result["parameters"] if p["path"].endswith(".mass"))["correct"]
    # Arrow ids are also arbitrary: compare measured endpoints, not id spelling.
    force = dict(
        id="F1",
        body="B1",
        tail=[100.0, 100.0],
        head=[150.0, 100.0],
        label="F",
        magnitude=dict(number=10.0, unit="N", status="given", source="ocr", confidence=1.0),
    )
    gold["forces"] = [force]
    prediction["forces"] = [{**copy.deepcopy(force), "id": "renamed_arrow"}]
    result = compare_scenes(prediction, gold)
    assert next(p for p in result["parameters"] if p["path"] == "forces.F1.magnitude")["correct"]
    raw = copy.deepcopy(gold)
    del raw["bodies"][0]["mass"]
    path = tmp_path / "TEST-scene-payload.json"
    path.write_text(json.dumps({"scene": raw}), encoding="utf-8")
    assert read_gold_scene(path)["bodies"][0]["mass"]["status"] == "assumed"


def test_existing_typescript_solver_is_the_only_trajectory_evaluator():
    gold = fixtures()["pendulum"].model_dump(mode="json", by_alias=True)
    changed = copy.deepcopy(gold)
    changed["constants"]["g"]["number"] = 1.0

    def pair(prediction):
        return dict(
            prediction=prediction, gold=gold, body_map={b["id"]: b["id"] for b in gold["bodies"]}
        )

    same, different = trajectories([pair(gold), pair(changed)])
    assert same["trajectory_correct"] and same["simulation_produced"]
    assert different["simulation_produced"] and not different["trajectory_correct"]


def test_detector_cache_is_local_independent_and_file_identity_sensitive(monkeypatch, tmp_path):
    detect = importlib.import_module("circuit_sim.backend.domains.mechanics.detect")
    import ultralytics

    path = tmp_path / "mechanics.pt"
    path.write_bytes(b"TEST only; loader is mocked")
    monkeypatch.setenv("MECHANICS_MODEL", str(path))
    builds = []

    def build(location):
        builds.append(Path(location))
        return SimpleNamespace(names=dict(enumerate(detect.NAMES)))

    monkeypatch.setattr(ultralytics, "YOLO", build)
    detect.release()
    try:
        first, _ = detect.detector()
        second, _ = detect.detector()
        assert first is second and builds == [path]
        path.write_bytes(b"different identity")
        third, _ = detect.detector()
        assert third is not first and len(detect._cache) == 1
        detect.release()
        monkeypatch.setattr(ultralytics, "YOLO", lambda *_: SimpleNamespace(names={0: "circuit"}))
        with pytest.raises(detect.WeightsUnavailable, match="incompatible"):
            detect.detector()
        assert not detect._cache
    finally:
        detect.release()
