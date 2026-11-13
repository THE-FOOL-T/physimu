"""Offline, cached version of AugmentedPhysics EasyOCRBanglaProvider."""

from functools import lru_cache
import time

from ..config import resolve_path
from ..inference import configure_threads
from ..ocr_tiles import windows, candidate_regions
from .normalize import record, to_native


@lru_cache(maxsize=2)
def local_reader(model_directory=None):
    configure_threads()
    import easyocr

    kwargs = {"model_storage_directory": model_directory} if model_directory else {}
    return easyocr.Reader(
        ["bn", "en"], gpu=False, detector=False, download_enabled=False, verbose=False, **kwargs
    )


class BanglaAdapter:
    name = "easyocr-bn"

    def __init__(self, config=None, reader=None):
        self.config = config or {}
        self.reader = reader

    def extract(self, image, run, components=None):
        if not run.available():
            return []
        directory = self.config.get("model_directory")
        reader = (
            self.reader
            if self.reader is not None
            else local_reader(str(resolve_path(directory)) if directory else None)
        )
        result = []
        # Keep native coordinates/glyph resolution. Pixel proposals feed the
        # recognizer directly; do not load/run a second full-image CRAFT detector.
        side = max(128, min(640, int(self.config.get("tile_side", 640))))
        if components:
            height, width = image.shape[:2]
            regions = []
            for component in components:
                a, b, c, d = component.bbox
                cx, cy = (a + c) / 2, (b + d) / 2
                half_width = max(320, (c - a) / 2 + 160)
                half_height = max(128, (d - b) / 2 + 80)
                left, top = max(0, int(cx - half_width)), max(0, int(cy - half_height))
                right, bottom = min(width, int(cx + half_width)), min(height, int(cy + half_height))
                for x, y, r, s in windows(image[top:bottom, left:right], side=side):
                    region = (left + x, top + y, left + r, top + s)
                    if region not in regions:
                        regions.append(region)
        else:
            regions = windows(image, side=side)
        for x, y, right, bottom in regions:
            if not run.available():
                break
            tile = image[y:bottom, x:right]
            # Independent pixel proposals keep recognition on text-sized patches. Do
            # not use RapidOCR detections as authority for Bengali coverage.
            proposal_image = tile.copy()
            for component in components or []:
                a, b, c, d = component.bbox
                proposal_image[
                    max(0, int(b - y)) : max(0, int(d - y)), max(0, int(a - x)) : max(0, int(c - x))
                ] = 255
            proposals = candidate_regions(proposal_image)
            groups = []
            for box in sorted(proposals, key=lambda p: p[0]):
                a, b, c, d = box
                group = next(
                    (
                        g
                        for g in groups
                        if min(d, g[3]) - max(b, g[1]) >= min(d - b, g[3] - g[1]) * 0.6
                        and max(a - g[2], g[0] - c, 0) <= max(12, min(d - b, g[3] - g[1]) * 0.8)
                    ),
                    None,
                )
                if group is None:
                    groups.append(list(box))
                else:
                    group[:] = [
                        min(a, group[0]),
                        min(b, group[1]),
                        max(c, group[2]),
                        max(d, group[3]),
                    ]
            if not groups and not components:
                groups = [[0, 0, right - x, bottom - y]]
            for a, b, c, d in sorted(groups, key=lambda p: (p[1], p[0])):
                if not run.available():
                    return result
                # Yield before starting a new native chunk when its expected
                # allowance no longer fits. Keep the loaded model reusable;
                # the process watchdog still stops an unexpectedly slow call.
                if time.monotonic() + self.config.get("call_reserve_seconds", 3) >= run.deadline:
                    run.diagnostics["work_limited"] = True
                    return result
                readings = reader.recognize(
                    tile[b:d, a:c], detail=1, paragraph=False, batch_size=1, workers=0
                )
                for polygon, text, confidence in readings:
                    if str(text).strip():
                        result.append(
                            record(
                                str(text),
                                to_native(polygon, c - a, d - b, offset=(x + a, y + b)),
                                confidence,
                                self.name,
                            )
                        )
                run.emit(result)
        return result
