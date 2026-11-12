"""Allow tests to run from either the workspace or circuit_sim root."""

import sys
from pathlib import Path
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from bootstrap import ensure_package

ensure_package()


def pytest_configure(config):
    # Keep test artifacts in this workspace; the host's shared temp directory
    # may be unavailable and must never need a permission change.
    if config.option.basetemp is None:
        root = Path(__file__).resolve().parents[2] / ".cache/pytest"
        root.mkdir(parents=True, exist_ok=True)
        config.option.basetemp = str(root / uuid.uuid4().hex)
