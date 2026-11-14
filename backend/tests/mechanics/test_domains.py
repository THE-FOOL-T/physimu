"""M1 domain boundaries, with the M5 perception stage contract."""

import ast
import base64
import importlib
import json
from pathlib import Path
import subprocess
import sys
import threading

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from circuit_sim.backend import core, domains
from circuit_sim.backend.app import main, warmup
from circuit_sim.backend.app.jobs import JobStore, STAGES
from circuit_sim.backend.domains.circuit import adapter
from circuit_sim.backend.domains.mechanics import MechanicsDomain
from circuit_sim.backend.domains.mechanics.engine import STAGES as MECHANICS_STAGES

ROOT = Path(__file__).resolve().parents[3]


def image():
    return np.full((80, 120, 3), 255, np.uint8)


def upload():
    return {"image": ("diagram.png", cv2.imencode(".png", image())[1].tobytes(), "image/png")}


def test_registry_defaults_and_unknown_name():
    assert domains.names() == ("circuit", "mechanics")
    assert domains.get("circuit").stages == STAGES
    assert isinstance(domains.get("mechanics"), MechanicsDomain)
    with pytest.raises(KeyError):
        domains.get("auto")


def test_registry_registers_without_silent_replacement(monkeypatch):
    monkeypatch.setattr(domains, "_registry", {})
    plugin = MechanicsDomain()
    domains.register(plugin)
    assert domains.get("mechanics") is plugin
    with pytest.raises(ValueError):
        domains.register(MechanicsDomain())
    assert domains.get("mechanics") is plugin


def test_circuit_adapter_calls_pipeline_in_process_and_preserves_keys(monkeypatch):
    original = {
        "netlist": {"warnings": []},
        "solution": {"warnings": []},
        "warnings": [],
        "timings": {"total": 1.25},
        "diagnostics": {"texts": []},
        "regions": [],
        "observed_netlist": {"image": {"path": ""}},
        "provenance": "partial",
        "future_key": {"keep": True},
    }
    received = []

    def analyze(*args, **kwargs):
        received.append((args, kwargs))
        kwargs["progress"]("detect")
        return original

    monkeypatch.setattr(adapter, "analyze_page", analyze)
    raster = image()
    stages = []
    result = adapter.CircuitDomain().analyze(
        raster,
        {"problem_text": "R = 4", "lang": "bn", "style": "printed", "use_label_reader": True},
        stages.append,
    )
    assert received[0][0][0] is raster
    assert received[0][0][1:] == ("R = 4", "bn", "printed")
    assert received[0][1]["use_label_reader"] is True
    assert stages == ["detect"]
    assert result == {**original, "domain": "circuit"}
    assert "domain" not in original


def test_mechanics_missing_model_is_explicit_with_original_image(monkeypatch, tmp_path):
    monkeypatch.setenv("MECHANICS_MODEL", str(tmp_path / "absent.pt"))
    stages = []
    result = MechanicsDomain().analyze(image(), {}, lambda stage, *_: stages.append(stage))
    assert result["domain"] == "mechanics"
    assert result["provenance"] == "unsupported"
    assert result["reason"] and any(w["code"] == "weights_unavailable" for w in result["warnings"])
    assert result["scene"]["bodies"] == []
    assert result["scene"]["meta"]["provenance"] == "unsupported"
    assert result["timings"]["total"] > 0
    assert set(stages) == set(MechanicsDomain().stages)
    assert all(
        result["timings"][s] is not None for s in ("text", "geometry", "associate", "validate")
    )
    assert result["diagnostics"]["stage_states"]["detect"]["status"] == "blocked"
    assert "solution" not in result and "netlist" not in result
    decoded = core.decode(base64.b64decode(result["source_image"].split(",")[1]))
    np.testing.assert_array_equal(decoded, image())


def test_domains_endpoint_has_real_stage_lists():
    response = TestClient(main.app).get("/api/domains")
    assert response.status_code == 200
    assert response.json() == {
        "domains": [
            {"name": name, "stages": list(domains.get(name).stages)} for name in domains.names()
        ]
    }


@pytest.mark.parametrize("route", ["/api/analyze", "/api/analyze/start"])
@pytest.mark.parametrize("name", ["unknown", "auto", ""])
def test_unknown_domain_is_typed_400_before_job_admission(route, name):
    response = TestClient(main.app).post(route, files=upload(), data={"domain": name})
    assert response.status_code == 400
    assert response.json()["detail"] == {
        "code": "unknown_domain",
        "message_key": "error.unknown_domain",
    }


@pytest.mark.parametrize("explicit", [False, True])
def test_api_circuit_default_and_explicit_keep_the_same_payload(monkeypatch, explicit):
    payload = {
        "netlist": {"warnings": []},
        "solution": {"warnings": []},
        "warnings": [],
        "extra": 7,
    }
    monkeypatch.setattr(adapter, "analyze_page", lambda *a, **k: payload)
    monkeypatch.setattr(warmup, "wait_for_models", lambda *_: None)
    response = TestClient(main.app).post(
        "/api/analyze", files=upload(), data={"domain": "circuit"} if explicit else {}
    )
    assert response.status_code == 200
    assert response.json() == {**payload, "domain": "circuit"}


@pytest.mark.parametrize("route", ["/api/analyze", "/api/analyze/start"])
def test_mechanics_api_never_enters_circuit_analysis_or_fallback(monkeypatch, tmp_path, route):
    from circuit_sim.backend.domains.mechanics import engine

    # This is a domain-routing contract on blank pixels. Test B separately runs
    # actual local OCR on the mandatory user raster without this controlled reader.
    monkeypatch.setattr(engine, "read_text", lambda *a, **k: ([], []))

    def forbidden(*args, **kwargs):
        pytest.fail("Mechanics entered circuit analysis")

    monkeypatch.setattr(adapter, "analyze_page", forbidden)
    monkeypatch.setattr(warmup, "wait_for_models", lambda *_: None)
    monkeypatch.setenv("MECHANICS_MODEL", str(tmp_path / "absent.pt"))
    client = TestClient(main.app)
    response = client.post(route, files=upload(), data={"domain": "mechanics", "lang": "bn"})
    assert response.status_code == 200
    data = response.json()
    if route.endswith("/start"):
        assert data["domain"] == "mechanics"
        assert data["stages"] == list(MECHANICS_STAGES)
        id_ = data["job_id"]
        try:
            main.jobs.jobs[id_]["future"].result(timeout=3)
            job = client.get("/api/analyze/" + id_).json()
            assert job["stage_count"] == len(MECHANICS_STAGES) and job["percent"] == 100
            assert set(job["history"]) == {"queued", *MECHANICS_STAGES}
            assert job["history"][-1] == "done"
            data = job["result"]
        finally:
            client.delete("/api/analyze/" + id_)
    assert data["provenance"] == "unsupported"
    assert data["domain"] == "mechanics" and data["reason"]
    assert any(w["code"] == "weights_unavailable" for w in data["warnings"])
    assert "solution" not in data and "netlist" not in data


def test_jobs_keep_independent_immutable_stages_and_default_circuit_progress():
    store = JobStore(limit=2)
    entered = [threading.Event(), threading.Event()]
    release = threading.Event()

    def runner(stage, index):
        def work(progress):
            progress(stage)
            entered[index].set()
            assert release.wait(3)
            return {"finished": True}

        return work

    custom = ["received", "geometry", "associate", "done"]
    try:
        mechanics = store.start(runner("associate", 0), stages=custom)
        circuit = store.start(runner("validate", 1))
        assert all(event.wait(3) for event in entered)
        custom.insert(1, "mutated_by_caller")
        a, b = store.get(mechanics), store.get(circuit)
        assert (a["stage_index"], a["stage_count"], a["percent"]) == (2, 4, 67)
        assert (b["stage_index"], b["stage_count"], b["percent"]) == (5, 9, 62)
        store.cancel(mechanics)
        release.set()
        for id_ in (mechanics, circuit):
            store.jobs[id_]["future"].result(timeout=3)
        assert store.get(mechanics)["error"]["code"] == "cancelled"
        assert store.get(mechanics)["result"] is None
        assert store.get(circuit)["percent"] == 100
        assert store.active == 0
    finally:
        release.set()
        store.executor.shutdown(wait=True)


@pytest.mark.parametrize("stages", [(), ("done",), ("received", "received", "done"), ("x", "done")])
def test_bad_stage_lists_do_not_consume_job_capacity(stages):
    store = JobStore(limit=1)
    try:
        with pytest.raises(ValueError):
            store.start(lambda _: {}, stages=stages)
        assert store.active == 0 and store.jobs == {}
    finally:
        store.executor.shutdown(wait=True)


def test_facade_reexports_original_shared_implementations():
    for module, names in {
        "config": ("load_config",),
        "pipeline.preprocess": ("decode", "preprocess", "figure_regions"),
        "pipeline.style": ("estimate_style",),
        "pipeline.text": ("read_text",),
        "app.jobs": ("JobStore", "Cancelled", "STAGES"),
    }.items():
        original = importlib.import_module("circuit_sim.backend." + module)
        for name in names:
            assert getattr(core, name) is getattr(original, name)


def test_mechanics_shared_imports_use_only_the_facade():
    for path in (ROOT / "backend/domains/mechanics").rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.ImportFrom) and node.level >= 3:
                assert node.level == 3 and node.module == "core", path


def test_new_domain_packages_are_installed_for_both_local_namespaces(tmp_path):
    code = """
import importlib, json
names = [f'{ns}.backend.{package}' for ns in ('augphys', 'circuit_sim')
         for package in ('core', 'domains', 'domains.circuit.adapter', 'domains.mechanics')]
print(json.dumps({name: importlib.import_module(name).__file__ for name in names}))
"""
    result = subprocess.run(
        [sys.executable, "-I", "-c", code], cwd=tmp_path, capture_output=True, text=True, check=True
    )
    for location in json.loads(result.stdout).values():
        assert Path(location).resolve().is_relative_to(ROOT)
