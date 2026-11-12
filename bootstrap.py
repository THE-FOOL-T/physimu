"""Resolve the public package name from any checkout directory name."""

import importlib.util
from pathlib import Path
import sys


def ensure_package():
    module = sys.modules.get("augphys") or sys.modules.get("circuit_sim")
    if module is None:
        root = Path(__file__).resolve().parent
        spec = importlib.util.spec_from_file_location(
            "augphys", root / "__init__.py", submodule_search_locations=[str(root)]
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules["augphys"] = module
        spec.loader.exec_module(module)
    # Compatibility names both expose the copied source, never another checkout.
    sys.modules.setdefault("augphys", module)
    sys.modules.setdefault("circuit_sim", module)
