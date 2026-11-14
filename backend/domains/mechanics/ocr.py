"""Mechanics candidate fusion over the shared local OCR engines' raw output.

The shared circuit semantic rank/erasure decisions never choose mechanics values.
Execution, budgets, engine isolation and offline configuration remain shared.
"""

import copy
import math

from .labels import parse, normalize


def fuse_mechanics(raw, diagnostics):
    items = diagnostics.get("engine_readings") or raw
    groups = []

    def same(a, b):
        x, y = a["bbox"], b["bbox"]
        shared = max(0.0, min(x[2], y[2]) - max(x[0], y[0])) * max(
            0.0, min(x[3], y[3]) - max(x[1], y[1])
        )

        def area(r):
            return max(1.0, (r[2] - r[0]) * (r[3] - r[1]))

        names = [{t.name for t in parse(r.get("text", "")) if t.name} for r in (a, b)]
        if all(names) and names[0] != names[1]:
            return False
        return shared / max(area(x), area(y)) >= 0.65

    for item in items[:512]:
        if not isinstance(item, dict) or len(item.get("bbox", [])) != 4:
            continue
        group = next((g for g in groups if all(same(item, other) for other in g)), None)
        if group is None:
            groups.append([item])
        else:
            group.append(item)

    def rank(row):
        tokens = parse(row.get("text", ""))
        return (sum(t.kind not in {"unplaced", "name"} for t in tokens), row.get("confidence", 0))

    result = []
    for group in groups:
        selected = max(group, key=rank)
        row = copy.deepcopy(selected)
        row["alternatives"] = copy.deepcopy(selected.get("alternatives", []))
        seen = {normalize(row.get("text", ""))}
        for candidate in group:
            if normalize(candidate.get("text", "")) not in seen:
                row["alternatives"].append(copy.deepcopy(candidate))
                seen.add(normalize(candidate.get("text", "")))
        row["provenance"] = list(
            dict.fromkeys(r.get("engine", r.get("source", "ocr")) for r in group)
        )
        classifier = selected.get("classifier_result")
        if (
            isinstance(classifier, (list, tuple))
            and classifier
            and isinstance(classifier[0], (list, tuple))
            and len(classifier[0]) == 2
            and str(classifier[0][0]) in {"0", "90", "180", "270"}
            and isinstance(classifier[0][1], (int, float))
            and math.isfinite(classifier[0][1])
            and 0.9 <= classifier[0][1] <= 1
        ):
            expected = int(classifier[0][0])
            if selected.get("rotation") == expected:
                for alternative in row["alternatives"]:
                    if alternative.get("rotation", expected) != expected:
                        alternative.update(
                            binding_eligible=False,
                            binding_exclusion="orientation_classifier_disagrees",
                        )
        result.append(row)
    return sorted(result, key=lambda r: (r["bbox"][1], r["bbox"][0]))
