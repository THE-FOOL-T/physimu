"""Automatic walking skeleton. Each optional reader can degrade independently."""

import base64
import time
import logging
from .associate import associate
from .resolve import resolve

import cv2
from .netlist import Netlist, Image, Meta, Node
from .budget import Budget, BudgetExpired
from .detect import detect
from .wires import trace, prepare_trace
from .validate import validate, fallback, safe_solve, score

log = logging.getLogger("circuit_sim.pipeline")


def image_url(image):
    ok, data = cv2.imencode(".png", image)
    if not ok:
        return ""
    return "data:image/png;base64," + base64.b64encode(data).decode()


def analyze_image(
    image,
    problem_text=None,
    lang="en",
    style="printed",
    detections=None,
    progress=None,
    use_label_reader=False,
    budget=None,
):
    budget = budget or Budget()
    report = progress or (lambda *a, **k: None)
    start = time.perf_counter()
    timings = {}
    warnings = []
    report("detect")
    try:
        components, annotations = (
            detections if detections is not None else detect(image, check=lambda: report("detect"))
        )
    except Exception as exc:
        log.exception("Pipeline detect failed: %s", type(exc).__name__)
        components = []
        annotations = []
        warnings.append(("detector_unavailable", None))
    timings["detect"] = time.perf_counter() - start
    source_url = image_url(image)
    report(
        "text",
        {
            "components": [c.model_dump(mode="json") for c in components],
            "source_image": source_url,
            "width": image.shape[1],
            "height": image.shape[0],
        },
    )
    texts = []
    ocr_diagnostics = {}
    try:
        from .text import read_text
        from ..config import load_config

        configuration = load_config()
        reserve = (
            configuration.get("analysis", {}).get("hybrid_reserve_seconds", 10)
            if str(configuration["ocr"]["backend"]).strip().lower() == "hybrid"
            else 0
        )

        texts, text_warnings = read_text(
            image,
            handwritten=style == "handwritten",
            use_label_reader=use_label_reader,
            components=components,
            diagnostics=ocr_diagnostics,
            check=lambda: report("text"),
            deadline=budget.deadline("text", reserve=reserve),
        )
        warnings.extend(text_warnings)
    except Exception as exc:
        from .ocr_regions import failure

        failure(ocr_diagnostics, "text", exc)
        warnings.append(("ocr_failed", None))
    timings["text"] = time.perf_counter() - start - timings["detect"]
    if not components:
        net = fallback()
        net.meta.problem_text = problem_text
        net.meta.language = lang
        for code, ref in warnings:
            net.warn(code, ref)
        report("solve")
        _, solution = safe_solve(net)
        return {
            "netlist": net.as_dict(),
            "solution": solution,
            "warnings": solution["warnings"],
            "source_image": source_url,
            "timings": {**timings, "total": time.perf_counter() - start},
            "regions": [],
            "provenance": "demo_fallback",
            "diagnostics": {"texts": texts, **ocr_diagnostics},
        }
    warnings.extend(associate(components, texts))
    if not problem_text:
        # Keep actual OCR prose as evidence; never generate missing problem text.
        from .ocr_regions import paragraph_text

        problem_text = paragraph_text(texts) or None
    candidates = []
    report("wires")
    trace_diagnostics = {}
    candidate_diagnostics = []

    def wire_check():
        report("wires")
        budget.check("wires")

    for alternative, repair in [(False, False), (False, True), (True, True)]:
        if not budget.available("wires"):
            break
        report("wires")
        import copy

        cs = copy.deepcopy(components)
        try:
            prepared = prepare_trace(
                image,
                cs,
                texts,
                annotations,
                handwritten=style == "handwritten",
                alternative=alternative,
                repair=repair,
                check=wire_check,
            )
            diagnostic = {"alternative_threshold": alternative, "repair": repair}
            nodes, graph, ws = trace(
                image,
                cs,
                texts,
                annotations,
                handwritten=style == "handwritten",
                prepared=prepared,
                diagnostics=diagnostic,
                check=wire_check,
            )
        except BudgetExpired:
            break
        net = Netlist(
            image=Image(path=source_url, width=image.shape[1], height=image.shape[0]),
            components=cs,
            nodes=nodes,
            wire_graph=graph,
            meta=Meta(problem_text=problem_text, language=lang, style=style),
        )
        for code, ref in warnings + ws:
            net.warn(code, ref)
        report("validate")
        net = validate(net)
        candidates.append(net)
        candidate_diagnostics.append(diagnostic)
        if score(net) == 0:
            break
    if not candidates:
        cs = [c.model_copy(deep=True) for c in components]
        nodes = []
        for c in cs:
            for terminal in c.terminals:
                terminal.node = "isolated." + terminal.id
                nodes.append(Node(id=terminal.node))
        partial = Netlist(
            image=Image(path=source_url, width=image.shape[1], height=image.shape[0]),
            components=cs,
            nodes=nodes,
            meta=Meta(
                problem_text=problem_text,
                language=lang,
                style=style,
                provenance="partial",
                degraded=True,
            ),
        )
        for code, ref in warnings:
            partial.warn(code, ref)
        candidates.append(validate(partial))
        candidate_diagnostics.append({"budget_exceeded": True})
    net = min(candidates, key=score)
    trace_diagnostics = candidate_diagnostics[candidates.index(net)]
    report("validate")
    if score(net) > 5 and budget.available("recovery") and budget.available("wires"):
        # A second detector pass can recover missed small symbols. Do not accept
        # more boxes merely because they exist: keep the lower-violation graph.
        report("detect")
        try:
            from .retry import recover

            def recovery_check():
                report("detect")
                budget.check("recovery")

            recovered, extra = recover(image, components, annotations, detect, check=recovery_check)
            if len(recovered) > len(components):
                associate(recovered, texts, weight=1.8)
                report("wires")
                recovered_diagnostics = {}
                ns, wg, ws = trace(
                    image,
                    recovered,
                    texts,
                    extra,
                    handwritten=style == "handwritten",
                    diagnostics=recovered_diagnostics,
                    check=wire_check,
                )
                alternative = Netlist(
                    image=net.image,
                    components=recovered,
                    nodes=ns,
                    wire_graph=wg,
                    meta=net.meta,
                )
                for code, ref in warnings + ws:
                    alternative.warn(code, ref)
                report("validate")
                alternative = validate(alternative)
                if score(alternative) < score(net):
                    net = alternative
                    trace_diagnostics = recovered_diagnostics
        except BudgetExpired:
            net.warn("time_budget")
        except Exception as exc:
            log.exception("Pipeline recovery failed: %s", type(exc).__name__)
            net.warn("recovery_failed")
    from .values import normalize
    import math

    for item in texts:
        marker = normalize(item["text"]).strip()
        if marker not in {"A", "B", "P", "Q"} or not net.wire_graph.points:
            continue
        box = item["bbox"]
        xy = ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)
        point = min(net.wire_graph.points, key=lambda p: math.dist(xy, p.xy))
        if math.dist(xy, point.xy) < min(image.shape[:2]) * 0.2:
            next(n for n in net.nodes if n.id == point.node).label = marker
    if budget.exceeded or time.monotonic() >= budget.end:
        net.warn("time_budget")
    for code, ref in associate(net.components, texts):
        net.warn(code, ref)
    report("resolve")
    net = resolve(net)
    for component in net.components:
        if component.value.status == "assumed" and component.value.source == "prior":
            net.warn("value_not_found", component.id)
    report("solve")
    observed = net.as_dict()
    net, solution = safe_solve(net)
    provenance = (
        "demo_fallback"
        if net.meta.provenance == "demo_fallback"
        else "partial"
        if net.meta.provenance == "partial" or any(c.disabled for c in net.components)
        else "extracted"
    )
    net.meta.provenance = provenance
    timings["total"] = time.perf_counter() - start
    return {
        "netlist": net.as_dict(),
        "solution": solution,
        "warnings": solution["warnings"],
        "timings": timings,
        "observed_netlist": observed,
        "source_image": source_url,
        "regions": [],
        "provenance": provenance,
        "diagnostics": {"texts": texts, "trace": trace_diagnostics, **ocr_diagnostics},
    }


def analyze_page(
    image,
    problem_text=None,
    lang="en",
    style="auto",
    progress=None,
    use_label_reader=False,
    budget=None,
):
    budget = budget or Budget()
    from .image_edges import image_edge_cut

    edge_cut = image_edge_cut(image)
    from .preprocess import preprocess, figure_regions
    import copy

    start = time.perf_counter()
    stage_times = {}
    current = None
    stage_started = start

    def report(stage, partial=None):
        nonlocal current, stage_started
        now = time.perf_counter()
        if stage != current:
            if current:
                stage_times[current] = stage_times.get(current, 0) + now - stage_started
            current = stage
            stage_started = now
        if progress:
            progress(stage, partial)

    def finish(result):
        if budget.exceeded or time.monotonic() >= budget.end:
            for target in [result["netlist"]["warnings"], result["warnings"]]:
                target.append(
                    {"code": "time_budget", "ref": None, "message_key": "warn.time_budget"}
                )
        if edge_cut:
            warning = {
                "code": "image_edge_cut",
                "ref": None,
                "message_key": "warn.image_edge_cut",
            }
            for target in [result["netlist"]["warnings"], result["warnings"]]:
                if warning not in target:
                    target.append(warning)
        report("done")
        result["timings"] = {**stage_times, "total": time.perf_counter() - start}
        return result

    report("preprocess")
    from .style import estimate_style

    estimated = estimate_style(image)
    image, quality_warnings, detected_style = preprocess(image, style, estimate=estimated)
    report("detect")
    budget.deadline("detect")
    try:
        components, annotations = detect(image, check=lambda: report("detect"))
        boxes = figure_regions(image, components)
    except Exception as exc:
        log.exception("Page detector failed: %s", type(exc).__name__)
        result = analyze_image(
            image,
            problem_text,
            lang,
            detected_style,
            detections=([], []),
            progress=report,
            use_label_reader=use_label_reader,
            budget=budget,
        )
        for target in [result["netlist"]["warnings"], result["warnings"]]:
            target.append(
                {
                    "code": "detector_unavailable",
                    "ref": None,
                    "message_key": "warn.detector_unavailable",
                }
            )
        result["style_estimate"] = {
            **estimated,
            "effective_style": detected_style,
            "override": style != "auto",
        }
        return finish(result)
    results = []
    for x1, y1, x2, y2 in boxes:
        if results and not budget.available("page"):
            break
        cs = copy.deepcopy(
            [
                c
                for c in components
                if x1 <= (c.bbox[0] + c.bbox[2]) / 2 < x2 and y1 <= (c.bbox[1] + c.bbox[3]) / 2 < y2
            ]
        )
        for c in cs:
            c.bbox = tuple(v - (x1 if i % 2 == 0 else y1) for i, v in enumerate(c.bbox))
            for t in c.terminals:
                t.xy = (t.xy[0] - x1, t.xy[1] - y1)
        anns = []
        for a in annotations:
            if (
                x1 <= (a["bbox"][0] + a["bbox"][2]) / 2 < x2
                and y1 <= (a["bbox"][1] + a["bbox"][3]) / 2 < y2
            ):
                a = copy.deepcopy(a)
                a["bbox"] = [v - (x1 if i % 2 == 0 else y1) for i, v in enumerate(a["bbox"])]
                anns.append(a)
        result = analyze_image(
            image[y1:y2, x1:x2],
            problem_text,
            lang,
            detected_style,
            (cs, anns),
            progress=report,
            use_label_reader=use_label_reader,
            budget=budget,
        )
        for code, ref in quality_warnings:
            warning = {"code": code, "ref": ref, "message_key": "warn." + code}
            result["netlist"]["warnings"].append(warning)
            result["warnings"].append(warning)
        result["netlist"]["meta"]["region"] = [x1, y1, x2, y2]
        results.append(result)
    results.sort(key=lambda r: -len(r["netlist"]["components"]))
    output = dict(results[0])
    output["regions"] = (
        [{"netlist": r["netlist"], "solution": r["solution"]} for r in results]
        if len(results) > 1
        else []
    )
    output["timings"]["total"] = time.perf_counter() - start
    output["style_estimate"] = {
        **estimated,
        "effective_style": detected_style,
        "override": style != "auto",
    }
    return finish(output)
