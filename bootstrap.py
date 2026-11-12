"""Resolve the public package name from any checkout directory name."""

import importlib.util
from pathlib import Path
import sys


def ensure_package():
    if "circuit_sim" not in sys.modules:
        root = Path(__file__).resolve().parent
        spec = importlib.util.spec_from_file_location(
            "circuit_sim", root / "__init__.py", submodule_search_locations=[str(root)]
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules["circuit_sim"] = module
        spec.loader.exec_module(module)
