import os
from pathlib import Path
import shutil
import subprocess
import sys

from circuit_sim.backend.config import load_config
from circuit_sim.backend import config


def test_clean_checkout_defaults_use_only_bundled_models(monkeypatch, tmp_path):
    shutil.copyfile(config.ROOT / "config.example.yaml", tmp_path / "config.example.yaml")
    monkeypatch.setattr(config, "ROOT", tmp_path)
    for key in list(os.environ):
        if key.startswith("CIRCUIT_"):
            monkeypatch.delenv(key)
    cfg = load_config()
    assert cfg["ocr"]["backend"] == "hybrid"
    assert cfg["inference"]["threads"] == 2
    paths = [cfg["detector"]["weights"], cfg["ocr"]["bangla"]["model_directory"]]
    paths.extend(cfg["ocr"]["rapidocr"][key] for key in ("detector", "recognizer", "classifier"))
    assert all(config.resolve_path(path).is_relative_to(tmp_path / "models") for path in paths)


def test_environment_paths(monkeypatch, tmp_path):
    monkeypatch.setenv("CIRCUIT_MODEL", str(tmp_path / "not-installed.pt"))
    monkeypatch.setenv("CIRCUIT_IMAGES", str(tmp_path / "images"))
    monkeypatch.setenv("CIRCUIT_EXTRA_IMAGES", str(tmp_path / "extra"))
    cfg = load_config()
    assert cfg["detector"]["weights"] == str(tmp_path / "not-installed.pt")
    assert cfg["images"] == str(tmp_path / "images")
    assert cfg["additional_images"] == str(tmp_path / "extra")


def test_import_from_arbitrary_folder_without_install(tmp_path):
    root = Path(__file__).resolve().parents[2]
    clone = tmp_path / "any-folder-name"
    clone.mkdir()
    for name in ["bootstrap.py", "__init__.py"]:
        shutil.copyfile(root / name, clone / name)
    (clone / "backend").mkdir()
    shutil.copyfile(root / "backend/__init__.py", clone / "backend/__init__.py")
    env = dict(os.environ, PYTHONPATH="")
    code = "from bootstrap import ensure_package; ensure_package(); import circuit_sim.backend; print(circuit_sim.__path__[0])"
    result = subprocess.run(
        [sys.executable, "-S", "-c", code],
        cwd=clone,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    assert str(clone) in result.stdout
