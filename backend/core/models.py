"""Application detector ownership; implementations remain in their domains."""

from contextlib import contextmanager
import gc
import threading

_lock = threading.RLock()
_local = threading.local()


def _release_circuit():
    from ..domains.circuit.detect import LOCK, detector

    with LOCK:
        detector.cache_clear()


_releases = {"circuit": _release_circuit}


def register_model_release(domain, release):
    with _lock:
        _releases[domain] = release


@contextmanager
def model_lease(domain, check=lambda: None):
    """Serialize service use and finish startup warmup before evicting its model."""
    if getattr(_local, "domain", None) == domain:
        check()
        yield
        return
    if getattr(_local, "domain", None):
        raise RuntimeError("Nested analysis of different domains is not supported")
    while not _lock.acquire(timeout=0.05):
        check()
    try:
        from ..app.warmup import wait_for_models

        wait_for_models(check)
        for other, release in list(_releases.items()):
            if other != domain:
                release()
        gc.collect()
        _local.domain = domain
        yield
    finally:
        _local.domain = None
        _lock.release()
