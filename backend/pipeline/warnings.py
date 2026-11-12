"""Stable, deduplicated evidence; the UI can group these without losing references."""

PRIORITY = {
    code: rank
    for rank, code in enumerate(
        [
            "source_open_loop",
            "solve_failed",
            "uncertain_topology",
            "dangling_wire",
            "missed_component",
            "crossing_uncertain",
            "value_not_found",
            "unit_inferred",
            "polarity_assumed",
            "time_budget",
        ]
    )
}


def ordered(warnings):
    unique = {(item["code"], item.get("ref")): item for item in warnings}
    return sorted(
        unique.values(),
        key=lambda item: (PRIORITY.get(item["code"], 50), item["code"], item.get("ref") or ""),
    )
