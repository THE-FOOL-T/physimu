"""One process-wide Torch setting, configured before model construction."""

import os
import threading
from .config import load_config

_lock = threading.Lock()
_configured = None


def thread_count():
    value = os.getenv("CIRCUIT_THREADS") or load_config().get("inference", {}).get("threads")
    return max(1, int(value)) if value is not None else max(1, (os.cpu_count() or 1) // 2)


def configure_threads():
    global _configured
    with _lock:
        if _configured is None:
            import torch

            _configured = thread_count()
            torch.set_num_threads(_configured)
    return _configured
