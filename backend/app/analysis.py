"""Shared synchronous/job execution and final evidence normalization."""

import logging
import threading
from ..pipeline.engine import analyze_page, image_url
from ..pipeline.validate import fallback, safe_solve
from ..pipeline.warnings import ordered
from ..domains.circuit.adapter import CircuitDomain
from ..core.models import model_lease

log = logging.getLogger("circuit_sim.analysis")
HYBRID_ANALYSIS_LOCK = threading.Lock()


def _run_analysis(
    decoded,
    problem_text,
    lang,
    style,
    use_label_reader=False,
    progress=None,
    request_id=None,
    domain=None,
):
    options = dict(
        problem_text=problem_text, lang=lang, style=style, use_label_reader=use_label_reader
    )
    if domain is not None and domain.name != "circuit":
        # The model lease handles startup ownership; mechanics never enters circuit
        # analysis, result normalization, or demo fallback.
        return domain.analyze(decoded, options, progress)

    from ..config import load_config
    from .warmup import wait_for_models

    def queued():
        if progress:
            progress("queued")

    acquired = False
    try:
        wait_for_models(queued)
        if str(load_config()["ocr"]["backend"]).strip().lower() == "hybrid":
            # Two admitted uploads must not spend their OCR deadlines waiting
            # on each other. Queue CPU analyses before starting the page clock.
            while not HYBRID_ANALYSIS_LOCK.acquire(timeout=0.05):
                queued()
            acquired = True
        result = (domain or CircuitDomain(analyze_page)).analyze(decoded, options, progress)
    except Exception as exc:
        log.exception("Analysis failed request_id=%s error_type=%s", request_id, type(exc).__name__)
        net = fallback(code="pipeline_degraded")
        net.meta.language = lang
        net, solution = safe_solve(net)
        result = {
            "netlist": net.as_dict(),
            "solution": solution,
            "warnings": solution["warnings"],
            "timings": {},
            "source_image": image_url(decoded),
            "regions": [],
            "provenance": "demo_fallback",
        }
    finally:
        if acquired:
            HYBRID_ANALYSIS_LOCK.release()
    for record in [result, *result.get("regions", [])]:
        if "netlist" in record:
            record["netlist"]["warnings"] = ordered(record["netlist"]["warnings"])
        if "solution" in record:
            record["solution"]["warnings"] = ordered(record["solution"]["warnings"])
    result["warnings"] = ordered(result["warnings"])
    if "observed_netlist" in result:
        result["observed_netlist"]["image"]["path"] = ""
    result["domain"] = "circuit"
    return result


def run_analysis(
    decoded,
    problem_text,
    lang,
    style,
    use_label_reader=False,
    progress=None,
    request_id=None,
    domain=None,
):
    def check():
        if progress:
            progress("queued")

    with model_lease(domain.name if domain is not None else "circuit", check):
        return _run_analysis(
            decoded, problem_text, lang, style, use_label_reader, progress, request_id, domain
        )
