"""Exercise the real HTTP analysis endpoint; no accuracy claims without gold netlists."""

import argparse
import collections
import json
from pathlib import Path
import statistics
import time
import httpx
import numpy as np

ROOT = Path(__file__).resolve().parents[2]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="http://127.0.0.1:8000")
    p.add_argument("--count", type=int, default=20)
    p.add_argument("--images")
    args = p.parse_args()
    from ..core.config import load_config

    cfg = load_config()
    base = Path(args.images or cfg["images"])
    paths = sorted(
        p for p in base.rglob("*") if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    )[: args.count]
    if not paths:
        raise SystemExit("No images found. Set CIRCUIT_IMAGES or pass --images.")
    health = httpx.get(args.url + "/api/health", timeout=10).json()
    if health.get("detector") == "warming" or health.get("ocr") == "warming":
        raise SystemExit(
            "Models are still warming. Wait for /api/health before measuring warm latency."
        )
    records = []
    for path in paths:
        start = time.perf_counter()
        try:
            with path.open("rb") as f:
                r = httpx.post(
                    args.url + "/api/analyze",
                    files={"image": (path.name, f)},
                    timeout=120,
                )
            data = r.json()
            net = data["netlist"]
            sol = data["solution"]
            records.append(
                {
                    "image": path.name,
                    "status": r.status_code,
                    "seconds": time.perf_counter() - start,
                    "components": len(net["components"]),
                    "simulation_produced": bool(sol["components"]),
                    "degraded": net["meta"]["degraded"],
                    "nonzero_current": any(
                        abs(c["current"]) > 1e-10 for c in sol["components"].values()
                    ),
                    "provenance": data.get("provenance"),
                    "stage_timings": data.get("timings", {}),
                    "warnings": dict(collections.Counter(w["code"] for w in data["warnings"])),
                    "kcl_error": sol["invariants"]["max_kcl_error"],
                    "power_error": sol["invariants"]["relative_power_error"],
                }
            )
        except Exception as exc:
            records.append(
                {
                    "image": path.name,
                    "simulation_produced": False,
                    "error": type(exc).__name__,
                }
            )
        print(json.dumps(records[-1]), flush=True)
    write_report(records, health)


def write_report(records, health):
    (ROOT / "docs/smoke.json").write_text(json.dumps(records, indent=2), encoding="utf-8")
    seconds = [r["seconds"] for r in records if "seconds" in r]
    summary = {
        "count": len(records),
        "produced": sum(r["simulation_produced"] for r in records),
        "degraded": sum(r.get("degraded", False) for r in records),
        "provenance": dict(collections.Counter(r.get("provenance", "error") for r in records)),
        "median_seconds": statistics.median(seconds) if seconds else None,
        "p95_seconds": float(np.percentile(seconds, 95)) if seconds else None,
        "max_seconds": max(seconds) if seconds else None,
        "over_10_seconds": sum(s > 10 for s in seconds),
        "warmup_seconds": health.get("warmup_seconds"),
        "end_to_end_accuracy": None,
    }
    pipeline = [
        r["stage_timings"]["total"]
        for r in records
        if r.get("stage_timings", {}).get("total") is not None
    ]
    summary["pipeline_median_seconds"] = statistics.median(pipeline) if pipeline else None
    summary["pipeline_p95_seconds"] = float(np.percentile(pipeline, 95)) if pipeline else None
    (ROOT / "docs/smoke_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    stages = sorted(
        {stage for r in records for stage in r.get("stage_timings", {}) if stage != "total"}
    )

    def number(value):
        return "unmeasured" if value is None else f"{value:.3f}"

    report = (
        f"# CPU performance measurement\n\nWarm local HTTP analysis of {len(records)} owner seen textbook images. Simulation production is regression coverage, not recognition accuracy. Times include HTTP transfer/decode and a fresh client per request; per-stage pipeline timers exclude upload decode. No external AI reader used.\n\n"
        + f"Median: {number(summary['median_seconds'])} s; p95: {number(summary['p95_seconds'])} s; max: {number(summary['max_seconds'])} s; requests >10 s: {summary['over_10_seconds']}. Startup warm-up: {summary['warmup_seconds']} s. Pipeline-only median: {number(summary['pipeline_median_seconds'])} s; p95: {number(summary['pipeline_p95_seconds'])} s.\n\n|Stage|Median seconds|p95 seconds|\n|---|---:|---:|\n"
    )
    for stage in stages:
        values = [r["stage_timings"][stage] for r in records if stage in r.get("stage_timings", {})]
        report += f"|{stage}|{np.median(values):.4f}|{np.percentile(values, 95):.4f}|\n"
    report += (
        "\n|Image|HTTP seconds|Pipeline seconds|Provenance|Degraded|\n|---|---:|---:|---|---|\n"
    )
    for record in records:
        report += f"|{record['image']}|{number(record.get('seconds'))}|{number(record.get('stage_timings', {}).get('total'))}|{record.get('provenance', 'error')}|{record.get('degraded', 'unknown')}|\n"
    report += "\nRaw samples: smoke.json; summary: smoke_summary.json. Browser event-to-readout timing (excludes paint) is in performance.json. Full-page small-label OCR remains slower; see ocr_benchmark.md. Optional remote-reader latency is unmeasured.\n"
    (ROOT / "docs/performance.md").write_text(report, encoding="utf-8")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
