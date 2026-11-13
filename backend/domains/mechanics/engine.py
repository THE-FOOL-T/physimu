"""Image evidence -> editable scene. Unsupported is a result, never a demo."""

import math
import time

import numpy as np

from ...core import preprocess, estimate_style, figure_regions, read_text, image_url, model_lease
from .detect import detect, Detection, WeightsUnavailable
from .scene import Scene
from .labels import read_tokens
from .label_reader import read_fallback
from .associate import associate, centre
from .perception import blank, measure, calibrate
from .validate import interpretations, finalize, warning
from .archetypes import hypotheses
from .evidence import build_evidence
from .readiness import assess
from .ocr import fuse_mechanics
from .understanding import understand, select_region

STAGES = (
    "received",
    "preprocess",
    "detect",
    "text",
    "geometry",
    "associate",
    "archetype",
    "validate",
    "done",
)


def route_domain(image):
    return {"domain": None, "reason": "domain_unknown", "implemented": False}


def readings(rows, w, h):
    clean = []
    if not isinstance(rows, (list, tuple)):
        return clean
    for r in rows[:256]:
        if not isinstance(r, dict) or not isinstance(r.get("text"), str):
            continue
        box = r.get("bbox", [])
        if (
            not isinstance(box, (list, tuple))
            or len(box) != 4
            or not all(isinstance(n, (int, float)) and math.isfinite(n) for n in box)
        ):
            continue
        x, y, z, v = map(float, box)
        box = [max(0.0, x), max(0.0, y), min(float(w), z), min(float(h), v)]
        if box[0] >= box[2] or box[1] >= box[3]:
            continue
        try:
            confidence = float(r.get("confidence", 0.0))
        except (ValueError, TypeError):
            continue
        if not math.isfinite(confidence):
            continue
        row = {
            "text": r["text"][:1000],
            "bbox": box,
            "confidence": max(0.0, min(1.0, confidence)),
            "source": r.get("source", "ocr"),
            "engine": r.get("engine", "unknown"),
            "provenance": r.get("provenance", []),
        }
        row["alternatives"] = (
            readings(r.get("alternatives", [])[:4], w, h) if r.get("alternatives") else []
        )
        clean.append(row)
    return clean


def analyze_mechanics_page(
    image, options=None, progress=None, *, detector=None, text_reader=None, label_reader=None
):
    options = options or {}
    lang = options.get("lang", "en")
    if lang not in {"en", "bn"}:
        lang = "en"
    started = time.perf_counter()
    changed = started
    stage = "received"
    timings = {s: None for s in STAGES if s != "done"}
    diagnostics = {"detections": [], "texts": [], "measurements": {}, "alternatives": []}
    source = image
    scene = blank(source, lang)
    style = {}

    def check():
        if progress:
            progress(stage)

    def advance(name, partial=None):
        nonlocal stage, changed
        now = time.perf_counter()
        timings[stage] = now - changed
        stage = name
        changed = now
        if progress:
            progress(name, partial)

    def result(reason=None):
        nonlocal scene
        scene = Scene.model_validate(scene).model_dump(mode="json", by_alias=True)
        diagnostics["hypotheses"] = hypotheses(scene)
        evidence = build_evidence(scene, diagnostics)
        diagnostics["evidence"] = evidence.model_dump(mode="json")
        readiness = assess(scene, evidence)
        timings[stage] = time.perf_counter() - changed
        timings["total"] = time.perf_counter() - started
        advance("done")
        return dict(
            domain="mechanics",
            provenance=scene["meta"]["provenance"],
            reason=reason,
            scene=scene,
            warnings=scene["warnings"],
            timings=timings,
            source_image=image_url(source),
            style_estimate=style,
            diagnostics=diagnostics,
            readiness=readiness,
        )

    with model_lease("mechanics", check):
        if progress:
            progress("received", {"source_image": image_url(source), "domain": "mechanics"})
        advance("preprocess")
        style = estimate_style(source)
        # Mechanics binds source pixels to physical geometry. Shared perspective
        # warping/ruling erasure has no inverse transform contract, so keep the
        # decoded source untouched. Native geometry/OCR do their own local masks.
        override = options.get("style", "auto")
        effective = override if override in {"printed", "handwritten"} else style["style"]
        notes = []
        diagnostics["understanding"] = understand(source, style)
        style = {
            **style,
            "effective_style": effective,
            "override": options.get("style", "auto") != "auto",
        }
        scene = blank(source, lang, effective)
        if effective == "handwritten":
            warning(scene, "handwriting_edit_expected")
        for code, _ in notes:
            warning(scene, code)
        advance(
            "detect",
            {
                "source_image": image_url(source),
                "width": source.shape[1],
                "height": source.shape[0],
            },
        )
        try:
            detected = (detector or detect)(source, check=check)
        except WeightsUnavailable as error:
            warning(scene, error.code)
            return result(str(error))
        except Exception:
            warning(scene, "detector_failed")
            return result(
                "Mechanics detector failed; the source image remains available for authoring."
            )
        h, w = source.shape[:2]
        boxes = []
        for i, d in enumerate(detected[:300]):
            if isinstance(d, dict):
                d = Detection(**d)
            if len(d.bbox) != 4 or not np.isfinite([*d.bbox, d.confidence]).all():
                continue
            a, b, c, e = d.bbox
            rect = [
                max(0.0, float(a)),
                max(0.0, float(b)),
                min(float(w), float(c)),
                min(float(h), float(e)),
            ]
            if rect[0] < rect[2] and rect[1] < rect[3]:
                boxes.append(Detection(f"D{i + 1}", d.type, rect, max(0.0, min(1.0, d.confidence))))
        diagnostics["detections"] = [d.as_dict() for d in boxes]
        regions = figure_regions(
            source, [d for d in boxes if d.type in {"block", "ball", "bob", "cart", "pulley"}]
        )
        diagnostics["figure_regions"] = regions
        try:
            chosen = select_region(regions, options.get("figure_region"), w, h)
        except ValueError:
            warning(scene, "invalid_figure_region")
            return result("Choose a figure region inside the source image.")
        selected = [
            d
            for d in boxes
            if chosen[0] <= centre(d.bbox)[0] <= chosen[2]
            and chosen[1] <= centre(d.bbox)[1] <= chosen[3]
        ]
        advance("text", {"detections": diagnostics["detections"]})
        ocr = {}
        try:
            raw, ocr_notes = (text_reader or read_text)(
                source,
                handwritten=effective == "handwritten",
                use_label_reader=False,
                components=boxes,
                diagnostics=ocr,
                deadline=time.monotonic() + 16,
                check=check,
            )
        except Exception:
            raw = []
            ocr_notes = [("ocr_failed", None)]
        raw = readings(raw, w, h)
        raw_engines = readings(ocr.get("engine_readings", []), w, h)
        all_text = readings(fuse_mechanics(raw, {"engine_readings": raw_engines}), w, h)
        text = [
            r
            for r in all_text
            if chosen[0] <= centre(r["bbox"])[0] <= chosen[2]
            and chosen[1] <= centre(r["bbox"])[1] <= chosen[3]
        ]
        text, fallback_notes, fallback_diagnostics = read_fallback(
            source,
            text,
            selected,
            consent=options.get("use_label_reader") is True,
            reader=label_reader,
            check=check,
        )
        ocr_notes.extend(fallback_notes)
        diagnostics["label_reader"] = fallback_diagnostics
        diagnostics["texts"] = text
        diagnostics["ocr"] = {
            k: v
            for k, v in ocr.items()
            if k in {"stages", "budget_exceeded", "engine_timeouts", "engine_limits"}
        }
        advance("geometry", {"texts": text})
        measured, evidence, choices, confidences = measure(source, selected, lang, effective, check)
        measured["warnings"].extend(scene["warnings"])
        scene = measured
        scene["meta"]["region"] = list(map(float, chosen))
        if len(regions) > 1:
            warning(scene, "multiple_figures")
        for code, _ in ocr_notes:
            warning(scene, code)
        # Raw OCR is retained as real native labels, not replaced by parser guesses.
        for i, r in enumerate(text):
            scene["annotations"].append(
                dict(id=f"OCR{i + 1}", type="label", geometry=dict(text=r["text"], bbox=r["bbox"]))
            )
        diagnostics["measurements"] = {
            ref: {
                k: v
                for k, v in fit.items()
                if k
                in {
                    "confidence",
                    "residual_px",
                    "length_px",
                    "angle_deg",
                    "center",
                    "radius_px",
                    "coils",
                    "warning",
                    "detection_id",
                }
            }
            for ref, fit in evidence.items()
        }
        advance("associate")
        assignments = associate(scene, read_tokens(text), confidences)
        diagnostics["assignments"] = assignments
        for row in assignments:
            if not row["accepted"]:
                continue
            annotation = next(
                (
                    a
                    for a in scene["annotations"]
                    if a["id"].startswith("OCR") and a["geometry"].get("bbox") == row["bbox"]
                ),
                None,
            )
            if annotation:
                annotation["bound_to"] = row["path"]
                body = next((b for b in scene["bodies"] if b["id"] == row["ref"]), None)
                if body and annotation["id"] not in body["label_ids"]:
                    body["label_ids"].append(annotation["id"])
        advance("archetype")
        (scene, reason, confidence), alternatives = interpretations(scene, choices)
        diagnostics["alternatives"] = alternatives
        diagnostics["archetype_confidence"] = confidence
        scene = calibrate(scene, assignments, evidence)
        advance("validate")
        reason = finalize(scene, reason)
        if (
            len(regions) > 1
            and scene["archetype"] == "collision_1d"
            and options.get("figure_region") is None
        ):
            after_region = sorted(regions, key=lambda b: (b[0], b[1]))[1]

            def inside(rect):
                x, y = centre(rect)
                return (
                    after_region[0] <= x <= after_region[2]
                    and after_region[1] <= y <= after_region[3]
                )

            after_boxes = [d for d in boxes if inside(d.bbox)]
            after_text = [r for r in all_text if inside(r["bbox"])]
            after, _, _, after_confidences = measure(source, after_boxes, lang, effective, check)
            observed = associate(after, read_tokens(after_text), after_confidences)
            speeds = {r["ref"]: r for r in observed if r["accepted"] and r["kind"] == "speed"}
            checks = []
            for before, body in zip(
                sorted(scene["bodies"], key=lambda b: b["anchor"][0]),
                sorted(after["bodies"], key=lambda b: b["anchor"][0]),
            ):
                row = speeds.get(body["id"])
                if not row:
                    continue

                def owns_arrow(annotation):
                    tail = annotation["geometry"]["points"][0]
                    owner = min(after["bodies"], key=lambda b: math.dist(tail, b["anchor"]))
                    return owner["id"] == body["id"] and math.dist(tail, body["anchor"]) <= 120

                arrow = min(
                    (
                        a
                        for a in after["annotations"]
                        if a["id"].startswith("velocity") and owns_arrow(a)
                    ),
                    key=lambda a: math.dist(a["geometry"]["points"][0], body["anchor"]),
                    default=None,
                )
                sign = (
                    -1
                    if arrow
                    and arrow["geometry"]["points"][-1][0] < arrow["geometry"]["points"][0][0]
                    else 1
                )
                checks.append(
                    dict(
                        body=before["id"],
                        # A signed component already supplies its direction;
                        # a nonnegative speed uses its own body's drawn arrow.
                        velocity_x=row["number"] if row["number"] < 0 else sign * row["number"],
                        confidence=row["confidence"],
                        bbox=row["bbox"],
                    )
                )
            if checks:
                scene["constraints"].append(
                    dict(
                        type="after_velocity",
                        refs=[r["body"] for r in checks],
                        values={
                            r["body"]: dict(
                                number=r["velocity_x"],
                                unit="m/s",
                                status="assumed",
                                source="ocr",
                                confidence=r["confidence"],
                            )
                            for r in checks
                        },
                    )
                )
            diagnostics["collision_panels"] = {
                "initial": chosen,
                "check": after_region,
                "observed": checks,
                "mapping": "left_to_right_assumed; object identities need review",
                "comparison": "frontend_solver_only",
            }
            warning(
                scene,
                "collision_check_available"
                if len(checks) == len(scene["bodies"])
                else "collision_check_unmeasured",
            )
            scene["meta"]["provenance"] = "partial"
        return result(reason)
