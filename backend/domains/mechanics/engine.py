"""Image evidence -> editable scene. Unsupported is a result, never a demo."""

import math
import time

import numpy as np

from ...core import preprocess, estimate_style, figure_regions, read_text, image_url, model_lease
from .detect import detect, Detection, WeightsUnavailable, checkpoint_readiness
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
from .classical import pendulum_proposals, annotate_alternatives
from ...core import configure_threads
from .stages import STAGES


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
        if r.get("rotation") in (0, 90, 180, 270):
            row["rotation"] = r["rotation"]
        classifier = r.get("classifier_result")
        if (
            isinstance(classifier, list)
            and classifier
            and isinstance(classifier[0], (list, tuple))
            and len(classifier[0]) == 2
            and str(classifier[0][0]) in {"0", "90", "180", "270"}
            and isinstance(classifier[0][1], (int, float))
            and math.isfinite(classifier[0][1])
            and 0 <= classifier[0][1] <= 1
        ):
            row["classifier_result"] = classifier[:1]
        if r.get("binding_eligible") is False:
            row["binding_eligible"] = False
            row["binding_exclusion"] = str(r.get("binding_exclusion", "orientation"))[:80]
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
    stage_states = {name: dict(id=name, status="pending") for name in STAGES}
    stage_states["received"]["status"] = "running"
    diagnostics["stage_states"] = stage_states
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
        if stage_states[stage]["status"] == "running":
            stage_states[stage]["status"] = "completed"
        stage = name
        stage_states[name]["status"] = "running"
        changed = now
        if progress:
            progress(
                name, {**(partial or {}), "stage_states": [dict(v) for v in stage_states.values()]}
            )

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
        stage_states["done"]["status"] = "completed"
        for entry in stage_states.values():
            if entry["status"] == "pending":
                entry.update(status="skipped", reason=reason or "not_executed")
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
        advance("understand")
        diagnostics["understanding"] = understand(source, style)
        advance(
            "detect",
            {
                "source_image": image_url(source),
                "width": source.shape[1],
                "height": source.shape[0],
            },
        )
        classical = None
        diagnostics["recognition"] = dict(
            method="controlled_perception" if detector else "model",
            model_status="checking",
            checkpoint=checkpoint_readiness(),
        )
        try:
            detected = (detector or detect)(source, check=check)
            diagnostics["recognition"]["model_status"] = "controlled" if detector else "ready"
            if not detector:
                diagnostics["recognition"]["checkpoint"] = checkpoint_readiness()
        except WeightsUnavailable as error:
            warning(scene, error.code)
            diagnostics["recognition"].update(model_status="unavailable", model_reason=str(error))
            detected = []
        except Exception:
            warning(scene, "detector_failed")
            diagnostics["recognition"].update(
                model_status="failed", model_reason="inference_failed"
            )
            detected = []
        if diagnostics["recognition"]["model_status"] not in {"ready", "controlled"}:
            configure_threads()
            detected, classical = pendulum_proposals(
                source, check, candidate=options.get("pendulum_candidate")
            )
            diagnostics["classical"] = classical
            diagnostics["recognition"]["method"] = "classical_vision" if detected else "unresolved"
            if detected:
                warning(scene, "classical_vision")
                stage_states["detect"].update(method="classical_vision", model_status="unavailable")
            else:
                stage_states["detect"].update(status="blocked", reason=classical["reason"])
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
                boxes.append(
                    Detection(
                        d.id if classical else f"D{i + 1}",
                        d.type,
                        rect,
                        max(0.0, min(1.0, d.confidence)),
                    )
                )
        diagnostics["detections"] = [
            {**d.as_dict(), "source": diagnostics["recognition"]["method"]} for d in boxes
        ]
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
        if ocr_notes:
            stage_states["text"].update(
                status="partial" if text else "failed",
                reason=",".join(code for code, _ in ocr_notes),
            )
        advance("geometry", {"texts": text})
        measured, evidence, choices, confidences = measure(
            source,
            selected,
            lang,
            effective,
            check,
            trace_min_pixels=3 if classical and classical["accepted"] else 8,
        )
        # Measure real model boxes first. A limited classical hypothesis may
        # recover a rejected topology; both evidence sources remain inspectable.
        if (
            not classical
            and not detector
            and interpretations(measured, choices)[0][0]["archetype"] == "unsupported"
        ):
            cv_boxes, cv_report = pendulum_proposals(
                source, check, candidate=options.get("pendulum_candidate")
            )
            diagnostics["classical"] = cv_report
            if cv_boxes:
                cv_scene, cv_evidence, cv_choices, cv_confidences = measure(
                    source, cv_boxes, lang, effective, check, trace_min_pixels=3
                )
                if interpretations(cv_scene, cv_choices)[0][0]["archetype"] == "pendulum":
                    diagnostics["model_detections"] = diagnostics["detections"]
                    diagnostics["model_geometry"] = measured
                    diagnostics["recognition"].update(
                        method="classical_vision",
                        selection_reason="model_topology_rejected_by_measured_geometry",
                    )
                    classical = cv_report
                    diagnostics["classical"] = classical
                    measured, evidence, choices, confidences = (
                        cv_scene,
                        cv_evidence,
                        cv_choices,
                        cv_confidences,
                    )
                    boxes = cv_boxes
                    regions = figure_regions(source, cv_boxes)
                    chosen = select_region(regions, options.get("figure_region"), w, h)
                    text = [
                        r
                        for r in all_text
                        if chosen[0] <= centre(r["bbox"])[0] <= chosen[2]
                        and chosen[1] <= centre(r["bbox"])[1] <= chosen[3]
                    ]
                    diagnostics["texts"] = text
                    diagnostics["figure_regions"] = regions
                    diagnostics["detections"] = [
                        {**d.as_dict(), "source": "classical_vision"} for d in cv_boxes
                    ]
                    warning(scene, "classical_vision")
        measured["warnings"].extend(scene["warnings"])
        scene = measured
        if classical and classical["accepted"]:
            annotate_alternatives(scene, classical)
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
        advance(
            "associate",
            {
                "scene_evidence": scene,
                "relationships": build_evidence(scene, diagnostics).model_dump(mode="json")[
                    "relationships"
                ],
            },
        )
        assignments = associate(scene, read_tokens(text), confidences)
        diagnostics["assignments"] = assignments
        if any(not r["accepted"] for r in assignments):
            stage_states["associate"].update(status="partial", reason="unplaced_parameters")
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
        if scene["archetype"] == "unsupported":
            stage_states["archetype"].update(status="blocked", reason=reason)
        scene = calibrate(scene, assignments, evidence)
        if classical and classical["accepted"]:
            body, link = scene["bodies"][0], scene["links"][0] if scene["links"] else None
            if body["mass"]["source"] == "prior":
                body["mass"].update(number=None)
                warning(scene, "missing_mass", body["id"])
            if link and not any(
                r["accepted"] and r["path"] == f"links.{link['id']}.length_m" for r in assignments
            ):
                link["length_m"].update(
                    number=None, status="assumed", source="prior", confidence=0.0
                )
                warning(scene, "missing_length", link["id"])
        advance("validate")
        reason = finalize(scene, reason)
        if scene["meta"]["provenance"] == "unsupported":
            stage_states["validate"].update(status="blocked", reason=reason)
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
