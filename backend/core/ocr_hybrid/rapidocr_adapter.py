"""AugmentedPhysics RapidOCR provider adapted to explicit offline models.

The unified API's final output hides the classifier's angle. Separate detection,
classification and recognition calls retain that evidence and avoid persistent
per-call flags (a bug already guarded against in the original provider).
"""

from functools import lru_cache
from pathlib import Path
import math

import cv2

from ..config import resolve_path
from ..inference import thread_count
from ..ocr_tiles import windows
from .normalize import parse, record, to_native


def model_file(value, name):
    if not value or not resolve_path(value).is_file():
        raise FileNotFoundError(
            f"Hybrid RapidOCR requires a local {name}; configure ocr.rapidocr.{name}"
        )
    return str(resolve_path(value))


@lru_cache(maxsize=2)
def local_engine(detector, recognizer, classifier, keys, threads):
    import onnxruntime as ort
    from rapidocr import RapidOCR, EngineType

    # A recognizer without embedded characters can otherwise trigger a dictionary
    # download even when all three model files exist. Verify before constructing.
    options = ort.SessionOptions()
    options.intra_op_num_threads = threads
    options.inter_op_num_threads = 1
    session = ort.InferenceSession(
        recognizer, sess_options=options, providers=["CPUExecutionProvider"]
    )
    if not session.get_modelmeta().custom_metadata_map.get("character") and not keys:
        raise ValueError("Recognizer lacks embedded characters; configure a local rec_keys_path")
    del session
    params = {
        "Det.model_path": detector,
        "Rec.model_path": recognizer,
        "Cls.model_path": classifier,
        "Det.engine_type": EngineType.ONNXRUNTIME,
        "Rec.engine_type": EngineType.ONNXRUNTIME,
        "Cls.engine_type": EngineType.ONNXRUNTIME,
        "EngineConfig.onnxruntime.intra_op_num_threads": threads,
        "EngineConfig.onnxruntime.inter_op_num_threads": 1,
        "EngineConfig.onnxruntime.use_cuda": False,
        "EngineConfig.onnxruntime.use_dml": False,
        "Global.log_level": "warning",
    }
    if keys:
        params["Rec.rec_keys_path"] = keys
    return RapidOCR(params=params)


def output_rows(output):
    """Normalize both output contracts inspected in the original provider."""
    if hasattr(output, "txts"):
        boxes = output.boxes if getattr(output, "boxes", None) is not None else []
        texts = output.txts if output.txts is not None else []
        scores = output.scores if output.scores is not None else []
        return list(zip(boxes, texts, scores))
    if isinstance(output, tuple) and len(output) == 2:
        return output[0] or []
    return output or []


def rotate(image, angle):
    return (
        image
        if angle == 0
        else cv2.rotate(
            image,
            {
                90: cv2.ROTATE_90_CLOCKWISE,
                180: cv2.ROTATE_180,
                270: cv2.ROTATE_90_COUNTERCLOCKWISE,
            }[angle],
        )
    )


class RapidOCRAdapter:
    name = "rapidocr"

    def __init__(self, config=None, engine=None):
        self.config = config or {}
        self.engine = engine

    def get_engine(self):
        if self.engine is not None:
            return self.engine
        paths = [
            model_file(self.config.get(key), key)
            for key in ("detector", "recognizer", "classifier")
        ]
        keys = self.config.get("rec_keys_path")
        keys = model_file(keys, "rec_keys_path") if keys else None
        return local_engine(*paths, keys, thread_count())

    def extract(self, image, run, components=None):
        if not run.available():
            return []
        engine = self.get_engine()
        result = []
        retries = 0
        regions = 0
        for tx, ty, tx2, ty2 in windows(image, components):
            if not run.available():
                break
            tile = image[ty:ty2, tx:tx2]
            detection = engine(tile, use_det=True, use_cls=False, use_rec=False)
            if getattr(detection, "boxes", None) is None:
                continue
            for polygon in detection.boxes:
                if not run.available() or regions >= self.config.get("max_regions", 64):
                    break
                regions += 1
                native = to_native(polygon, tx2 - tx, ty2 - ty, offset=(tx, ty))
                xs, ys = zip(*native)
                x, y = max(0, math.floor(min(xs))), max(0, math.floor(min(ys)))
                right, bottom = (
                    min(image.shape[1], math.ceil(max(xs))),
                    min(image.shape[0], math.ceil(max(ys))),
                )
                crop = image[y:bottom, x:right]
                if not crop.size:
                    continue
                base = 90 if crop.shape[0] > crop.shape[1] * 1.35 else 0
                if not run.available():
                    break
                classification = engine(
                    rotate(crop, base), use_det=False, use_cls=True, use_rec=False
                )
                classes = getattr(classification, "cls_res", None) or []
                flipped = bool(classes and "180" in classes[0][0] and classes[0][1] > 0.9)
                angle = (base + (180 if flipped else 0)) % 360

                def recognize(angle):
                    if not run.available():
                        return []
                    output = engine(rotate(crop, angle), use_det=False, use_cls=False, use_rec=True)
                    texts = output.txts if output.txts is not None else []
                    scores = output.scores if output.scores is not None else []
                    return [
                        record(
                            str(t),
                            native,
                            s,
                            self.name,
                            rotation=angle,
                            orientation_method="explicit_crop_rotation",
                            classifier_result=[
                                [str(label), float(score)] for label, score in classes
                            ],
                        )
                        for t, s in zip(texts, scores)
                        if str(t).strip()
                    ]

                readings = recognize(angle)
                result.extend(readings)
                run.emit(result)
                # Retry only uncertain regions, at most four per request. The
                # reversed 'digit =' failure from the source is covered here.
                value = parse(readings[0]["text"]) if readings else None
                if (
                    not value or (value["number"] is not None and not value["unit"])
                ) and retries < self.config.get("max_retry_regions", 4):
                    retries += 1
                    result.extend(recognize((angle + 180) % 360))
                    run.emit(result)
            if regions >= self.config.get("max_regions", 64):
                break
        return result
