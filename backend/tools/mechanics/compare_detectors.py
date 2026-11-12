"""A guarded per-class promotion decision; never promote smoke/synthetic validation."""

import argparse
import json
from pathlib import Path

from .common import NAMES, contained, write_json


def promotion(baseline, candidate, targets, common_min_support=25):
    reasons = []
    for item in (baseline, candidate):
        if item.get("origin") != "real" or not item.get("frozen_real") or item.get("smoke_only"):
            reasons.append(
                "Independent frozen real evaluation required; smoke/synthetic cannot be promoted"
            )
        if item.get("images", 0) < 20 or item.get("style") not in {"printed", "handwritten"}:
            reasons.append("A frozen partition needs at least 20 real images")
    if (
        baseline.get("protocol") != candidate.get("protocol")
        or baseline.get("image_sha256") != candidate.get("image_sha256")
        or baseline.get("style") != candidate.get("style")
    ):
        reasons.append("Identical images, partition and evaluation protocol required")
    if not targets or any(name not in NAMES for name in targets):
        reasons.append("Declare supported target classes before comparing")
    for name in NAMES:
        a = baseline.get("classes", {}).get(name, {})
        b = candidate.get("classes", {}).get(name, {})
        old, new = a.get("recall"), b.get("recall")
        if a.get("support") != b.get("support"):
            reasons.append(f"Support changed: {name}")
        if name in targets and (old is None or new is None or new <= old):
            reasons.append(f"No measured recall improvement: {name}")
        if (
            old is not None
            and new is not None
            and a.get("support", 0) >= common_min_support
            and new < old - 0.02 - 1e-12
        ):
            reasons.append(f"Common class regressed by more than two points: {name}")
    return {
        "eligible": not reasons,
        "reasons": sorted(set(reasons)),
        "targets": targets,
        "common_min_support": common_min_support,
        "rule": "Every declared target improves; no common class loses >0.02 recall. Both printed/handwritten partitions must pass separately.",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("baseline", type=Path)
    p.add_argument("candidate", type=Path)
    p.add_argument("--targets", nargs="+", required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    result = promotion(
        json.loads(a.baseline.read_text()), json.loads(a.candidate.read_text()), a.targets
    )
    write_json(contained(a.out), result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
