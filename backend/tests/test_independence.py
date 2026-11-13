"""The imported circuit is local source and remains usable without its origin."""

import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tomllib

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = "THE-FOOL-T/" + "circuit-sim"
# M1 explicitly authorizes these shared boundaries (plan-M1.md). Pipeline,
# solver, fixtures and every imported test source remain hash-protected.
M1_SHARED_FILES = {
    "backend/app/analysis.py",
    "backend/app/jobs.py",
    "backend/app/main.py",
    "frontend/src/main.ts",
    "frontend/src/ui/upload.ts",
    "frontend/src/ui/canvas-editor.ts",
    "frontend/src/ui/text-inspector.ts",
    "frontend/src/i18n/en.json",
    "frontend/src/i18n/bn.json",
}
M1_LAYOUT_SNAPSHOTS = {
    f"frontend/browser-tests/layout.spec.ts-snapshots/{width}-{lang}-{theme}.png"
    for width in (1440, 1024, 390)
    for lang in ("en", "bn")
    for theme in ("light", "dark")
}


def tracked_files():
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [ROOT / name for name in output.decode("utf-8").split("\0") if name]


def test_no_upstream_remote_submodule_or_linked_source():
    assert not (ROOT / ".gitmodules").exists()
    remotes = subprocess.check_output(["git", "remote", "-v"], cwd=ROOT).decode()
    assert UPSTREAM.lower() not in remotes.lower()
    for path in tracked_files():
        assert path.resolve().is_relative_to(ROOT)
        assert not path.is_symlink(), path


def test_no_weights_private_state_or_external_source_dependency_is_tracked():
    forbidden = {".pt", ".pth", ".onnx", ".npz", ".ckpt", ".safetensors"}
    for path in tracked_files():
        relative = path.relative_to(ROOT)
        assert path.suffix.lower() not in forbidden, relative
        assert not {".venv", "node_modules", ".cache", "dist"}.intersection(relative.parts)
        assert path.name != "config.local.yaml"
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert project["project"]["name"] == "augphys"
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    assert "circuit-sim" not in requirements
    assert "git+" not in requirements


def test_upstream_checkout_references_are_consolidated_in_import_note():
    remote = re.compile(r"https?://github[.]com/" + re.escape(UPSTREAM), re.I)
    checkout = re.compile(r"[A-Z]:[/\\]+Circuit Simu[/\\]+circuit_sim", re.I)
    for path in tracked_files():
        if path == ROOT / "docs/IMPORT.md":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        assert not remote.search(text), path.relative_to(ROOT)
        assert not checkout.search(text), path.relative_to(ROOT)


def test_public_and_compatibility_imports_resolve_inside_this_checkout(tmp_path):
    code = """
import importlib, json
names = ['augphys', 'augphys.backend.pipeline.engine',
         'circuit_sim', 'circuit_sim.backend.pipeline.engine']
print(json.dumps({name: importlib.import_module(name).__file__ for name in names}))
"""
    result = subprocess.run(
        [sys.executable, "-I", "-c", code],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=True,
    )
    for location in json.loads(result.stdout).values():
        assert Path(location).resolve().is_relative_to(ROOT), location


def test_circuit_implementation_fixtures_and_original_tests_match_import():
    manifest = json.loads((ROOT / "docs/import-manifest.json").read_text(encoding="utf-8"))
    prefixes = (
        "backend/",
        "frontend/src/",
        "frontend/tests/",
        "frontend/browser-tests/",
        "frontend/public/",
        "fixtures/",
    )
    for item in manifest["files"]:
        if item["path"] in M1_SHARED_FILES | M1_LAYOUT_SNAPSHOTS:
            continue
        if item["path"].startswith(prefixes):
            path = ROOT / item["path"]
            data = path.read_bytes()
            if "text_sha256_lf" in item:
                # Git's declared LF policy must also pass after a fresh checkout.
                data = data.replace(b"\r\n", b"\n")
            expected = item.get("text_sha256_lf", item["sha256"])
            assert hashlib.sha256(data).hexdigest() == expected, item["path"]
    original = next(item for item in manifest["files"] if item["path"] == "config.example.yaml")
    config = (ROOT / original["path"]).read_bytes()
    marker = b"\n# Mechanics M4: independent model; no runtime downloads.\n"
    prefix, separator, addition = config.partition(marker)
    # M4 explicitly adds mechanics configuration; every original config byte stays protected.
    assert separator and hashlib.sha256(prefix).hexdigest() == original["sha256"]
    import yaml

    assert yaml.safe_load(addition) == {
        "mechanics": {
            "weights": "models/mechanics.pt",
            "confidence": 0.25,
            "input_size": 640,
            "device": "cpu",
        }
    }


def test_circuit_analysis_transport_is_local_except_the_opt_in_label_reader():
    forbidden = {"httpx", "requests", "urllib", "aiohttp", "http.client"}
    for directory in (
        ROOT / "backend/pipeline",
        ROOT / "backend/solver",
        ROOT / "backend/app",
        ROOT / "backend/core",
        ROOT / "backend/domains",
    ):
        for path in directory.rglob("*.py"):
            if path.name == "label_reader.py" or path == ROOT / "backend/core/ocr_label_reader.py":
                continue
            for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
                if isinstance(node, ast.Import):
                    assert not forbidden.intersection(alias.name for alias in node.names), path
                if isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    assert node.module.split(".")[0] not in forbidden, path
    for path in (ROOT / "frontend/src").rglob("*.ts"):
        assert not re.search(r"fetch\(\s*['\"]https?://", path.read_text(encoding="utf-8")), path


def test_missing_detector_is_explicit_and_does_not_import_a_model(monkeypatch, tmp_path):
    from circuit_sim.backend.pipeline import detect, engine, text

    monkeypatch.setenv("CIRCUIT_MODEL", str(tmp_path / "missing.pt"))
    monkeypatch.setattr(text, "read_text", lambda *a, **k: ([], []))
    model_was_loaded = "ultralytics" in sys.modules
    detect.detector.cache_clear()
    try:
        result = engine.analyze_page(np.full((180, 240, 3), 255, dtype=np.uint8))
    finally:
        detect.detector.cache_clear()
    assert result["provenance"] == "demo_fallback"
    assert any(w["code"] == "detector_unavailable" for w in result["warnings"])
    assert result["source_image"].startswith("data:image/png;base64,")
    assert ("ultralytics" in sys.modules) == model_was_loaded


def test_model_formats_and_local_configuration_remain_ignored():
    paths = ["config.local.yaml", "models/owner.pt", "models/ocr/owner.onnx", "models/bn.pth"]
    result = subprocess.run(
        ["git", "check-ignore", *paths],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert set(result.stdout.splitlines()) == set(paths)
