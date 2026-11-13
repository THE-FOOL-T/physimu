"""Portable configuration: example defaults, private local overrides, environment."""

import os
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]


def load_config():
    cfg = yaml.safe_load((ROOT / "config.example.yaml").read_text(encoding="utf-8"))
    local = ROOT / "config.local.yaml"
    if local.is_file():
        for key, value in (yaml.safe_load(local.read_text(encoding="utf-8")) or {}).items():
            if isinstance(value, dict) and isinstance(cfg.get(key), dict):
                cfg[key].update(value)
            else:
                cfg[key] = value
    for name, key in [
        ("CIRCUIT_IMAGES", "images"),
        ("CIRCUIT_EXTRA_IMAGES", "additional_images"),
    ]:
        cfg[key] = os.getenv(name, cfg[key])
    cfg["detector"]["weights"] = os.getenv("CIRCUIT_MODEL", cfg["detector"]["weights"])
    ocr = cfg.setdefault("ocr", {})
    ocr["backend"] = os.getenv("CIRCUIT_OCR_BACKEND", ocr.get("backend", "legacy"))
    rapid = ocr.setdefault("rapidocr", {})
    for key, name in [
        ("detector", "CIRCUIT_RAPIDOCR_DET"),
        ("recognizer", "CIRCUIT_RAPIDOCR_REC"),
        ("classifier", "CIRCUIT_RAPIDOCR_CLS"),
        ("rec_keys_path", "CIRCUIT_RAPIDOCR_KEYS"),
    ]:
        rapid[key] = os.getenv(name, rapid.get(key))
    bangla = ocr.setdefault("bangla", {})
    bangla["model_directory"] = os.getenv("CIRCUIT_EASYOCR_MODELS", bangla.get("model_directory"))
    for key in ("images", "additional_images"):
        cfg[key] = str(resolve_path(cfg[key]))
    for key in ("weights", "original"):
        if cfg["detector"].get(key):
            cfg["detector"][key] = str(resolve_path(cfg["detector"][key]))
    return cfg


def resolve_path(value):
    path = Path(os.path.expandvars(os.path.expanduser(str(value))))
    return path if path.is_absolute() else ROOT / path
