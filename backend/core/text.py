"""Local bilingual OCR and a deliberately optional, pluggable handwriting reader."""

from functools import lru_cache
import os
import shutil
import threading
from .ocr_label_reader import LabelReader

LOCK = threading.Lock()

_vlm: LabelReader | None = None


def configure_label_reader(reader: LabelReader | None):
    global _vlm
    _vlm = reader


@lru_cache(maxsize=3)
def easy_reader(language="en", detection=True):
    from .inference import configure_threads

    configure_threads()
    import easyocr

    # No downloads on the automatic request path. Install/cache models explicitly.
    return easyocr.Reader(
        ["bn", "en"] if language == "bn" else ["en"],
        gpu=False,
        download_enabled=False,
        verbose=False,
        detector=detection,
    )


def read_text(
    image,
    handwritten=False,
    use_label_reader=False,
    components=None,
    diagnostics=None,
    deadline=None,
    check=None,
):
    from .config import load_config

    # The environment overrides the persistent selection in config.local.yaml.
    backend = str(load_config()["ocr"]["backend"]).strip().lower()
    if backend != "legacy":
        return _read_selected_backend(
            backend, image, use_label_reader, components, diagnostics, deadline, check
        )
    import time
    from .ocr_tiles import easy_tiles
    from .ocr_regions import failure, merge_readings

    diagnostics = diagnostics if diagnostics is not None else {}
    check = check or (lambda: None)
    deadline = deadline if deadline is not None else time.monotonic() + 16
    warnings = []
    items = []
    available = 0
    # Reserve time for each installed engine instead of selecting just one.
    binary = os.getenv("TESSERACT_CMD") or shutil.which("tesseract")
    if binary:
        try:
            from .tesseract_regions import recognize

            check()
            outputs = recognize(
                image, binary, components, min(deadline, time.monotonic() + 5), check
            )
            items.extend(outputs)
            available += 1
            diagnostics.setdefault("stages", []).append(
                {"stage": "tesseract", "status": "ready", "readings": len(outputs)}
            )
        except Exception as exc:
            failure(diagnostics, "tesseract", exc)
    else:
        diagnostics.setdefault("stages", []).append({"stage": "tesseract", "status": "unavailable"})
    try:
        check()
        acquired = False
        while time.monotonic() < deadline:
            check()
            if LOCK.acquire(timeout=min(0.05, max(0, deadline - time.monotonic()))):
                acquired = True
                break
        try:
            if not acquired:
                diagnostics["budget_exceeded"] = True
            else:
                reader = easy_reader("en")
                outputs = easy_tiles(
                    image,
                    reader,
                    lambda: easy_reader("bn", False),
                    components,
                    handwritten,
                    diagnostics=diagnostics,
                    deadline=deadline,
                    check=check,
                )
                items.extend(outputs)
                available += 1
                diagnostics.setdefault("stages", []).append(
                    {"stage": "easyocr", "status": "ready", "readings": len(outputs)}
                )
        finally:
            if acquired:
                LOCK.release()
    except Exception as exc:
        failure(diagnostics, "easyocr", exc)
    if not available:
        warnings.append(("ocr_unavailable", None))
    if any(stage["status"] == "failed" for stage in diagnostics.get("stages", [])):
        warnings.append(("ocr_partial" if available else "ocr_failed", None))
    if diagnostics.get("budget_exceeded") or time.monotonic() >= deadline:
        warnings.append(("time_budget", None))
    diagnostics["engine_readings"] = [dict(item) for item in items]
    if use_label_reader:
        from .ocr_label_reader import configured_reader, read_crops

        reader = _vlm or configured_reader()
        if reader is None:
            warnings.append(("label_reader_unavailable", None))
        else:
            extra, reader_warnings = read_crops(
                image, reader, items, deadline=deadline, check=check
            )
            items.extend(extra)
            warnings.extend(reader_warnings)
    return merge_readings(items), warnings


def _read_selected_backend(
    backend, image, use_label_reader, components, diagnostics, deadline, check
):
    import time
    from .config import load_config
    from .ocr_hybrid.router import read_hybrid, fuse

    diagnostics = diagnostics if diagnostics is not None else {}
    diagnostics["ocr_backend"] = backend
    check = check or (lambda: None)
    check()
    deadline = deadline if deadline is not None else time.monotonic() + 16
    if backend != "hybrid":
        diagnostics.setdefault("stages", []).append(
            {"stage": "ocr_backend", "status": "failed", "message": "Select legacy or hybrid OCR"}
        )
        return [], [("ocr_failed", None)]
    items, warnings = read_hybrid(
        image, components, diagnostics, deadline, check, LOCK, load_config().get("ocr", {})
    )
    if use_label_reader:
        from .ocr_label_reader import configured_reader, read_crops

        reader = _vlm or configured_reader()
        if reader is None:
            warnings.append(("label_reader_unavailable", None))
        else:
            extra, extra_warnings = read_crops(image, reader, items, deadline=deadline, check=check)
            for item in extra:
                item.update(ocr_backend="hybrid", engine="label-reader", wire_overlap=True)
            items = fuse([*items, *extra])
            warnings.extend(extra_warnings)
    check()
    return items, warnings
