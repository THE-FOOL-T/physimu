"""Independent mechanics settings, resolved locally through the shared facade."""

import os
from pathlib import Path

from ...core import load_config

ROOT = Path(__file__).resolve().parents[3]


def mechanics_config():
    cfg = dict(load_config()["mechanics"])
    raw = os.getenv("MECHANICS_MODEL", cfg["weights"])
    path = Path(os.path.expandvars(os.path.expanduser(str(raw))))
    cfg["weights"] = str((path if path.is_absolute() else ROOT / path).resolve())
    if not 0 <= float(cfg["confidence"]) <= 1 or int(cfg["input_size"]) < 32:
        raise ValueError("Invalid mechanics detector configuration")
    return cfg
