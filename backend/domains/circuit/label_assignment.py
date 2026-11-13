"""Global component/value matching with explicit rejection evidence."""

from ...core.matching import center, search_windows
import math
import re
import numpy as np
from scipy.optimize import linear_sum_assignment
from .netlist import Value, Polarity
from ...core.value_tokens import parse_value, component_unit


def label_allowed(component, value):
    label = value.get("label")
    if not label:
        return True
    if value.get("emf_symbol"):
        return component_unit(component.type) == "V"
    families = {
        "R": {"resistor", "rheostat", "lamp", "fuse"},
        "C": {"capacitor"},
        "L": {"inductor"},
        "V": {"dc_source", "voltage_source", "battery", "voltmeter"},
        "E": {"dc_source", "voltage_source", "battery"},
        "K": {"switch"},
        "S": {"switch"},
        "G": {"galvanometer"},
        "I": {"current_source", "ammeter"},
    }
    return component.type in families.get(label[0], {component.type})


def inference_supported(component, item, value, distance):
    if not value.get("unit_inferred"):
        return True
    x, y = center(item["bbox"])
    inside = any(a <= x <= c and b <= y <= d for a, b, c, d in search_windows(component))
    if (
        item.get("confidence", 0) < 0.35
        or not inside
        or distance > min(65, max(35, math.dist(*[t.xy for t in component.terminals]) * 0.5))
    ):
        return False
    # Unitless OCR on a lead/plate/zigzag must not become a fabricated value.
    raw = item["text"].strip()
    body = (
        component.bbox[0] <= x <= component.bbox[2] and component.bbox[1] <= y <= component.bbox[3]
    )
    supported_unit = any(
        note in value.get("normalizations", [])
        for note in ["contextual_unit_lookalike", "visual_unit_shape"]
    ) or value.get("has_prefix")
    if item.get("wire_overlap") and not supported_unit:
        return False
    if body and not supported_unit:
        return False
    if not supported_unit:
        if item.get("confidence", 0) < 0.65:
            return False
        for alternative in item.get("alternatives", []):
            other = parse_value(alternative["text"], component.type)
            if alternative.get("confidence", 0) < 0.3 or not other or other["number"] is None:
                continue
            # Conflicting bare readings (e.g. 332 / 30 / 39 for 3 ohm) need
            # human confirmation, even when one engine is very confident.
            scale = max(abs(value["number"]), abs(other["number"]), 1e-12)
            if abs(value["number"] - other["number"]) / scale > 0.2:
                return False
        a, b = [t.xy for t in component.terminals]
        length = max(1, math.dist(a, b))
        axis = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
        cx, cy = center(component.bbox)
        axial = abs((x - cx) * axis[0] + (y - cy) * axis[1])
        normal = abs((x - cx) * (-axis[1]) + (y - cy) * axis[0])
        minor = min(component.bbox[2] - component.bbox[0], component.bbox[3] - component.bbox[1])
        if axial > length * 0.35 and normal < minor * 0.5 + 8:
            return False
    return True


def parse_item(item, context=None):
    if item.get("ocr_backend") == "hybrid":
        from ...core.ocr_hybrid.normalize import parse

        return parse(item["text"], context)
    value = parse_value(item["text"], context)
    digits = re.sub(r"\s+", "", item["text"])
    if (
        component_unit(context) == "ohm"
        and item.get("unit_hint") == "ohm"
        and re.fullmatch(r"\d+", digits)
    ):
        count = item.get("glyph_count", 0) - 1
        if 0 < count < len(digits):
            value = parse_value(digits[:count] + " Ω", "resistor")
            value.update(unit_inferred=True, confidence=0.55)
            value["normalizations"].append("visual_unit_shape")
    return value


def associate(components, texts, weight=1.0):
    warnings = []
    confirmed = set()
    for index, item in enumerate(texts):
        if item.get("user_confirmed"):
            confirmed.add(index)
            continue
        item.pop("assigned_to", None)
        item.pop("role", None)
        item.pop("association", None)
        item.update(
            id=f"t{index + 1}",
            raw=item.get("raw_text", item["text"]),
            parsed=parse_item(item),
            assignments=[],
            outcome="unassigned",
            reason="not_selected",
            candidates=[],
        )
        if item["parsed"] is None:
            item.update(outcome="ignored", reason="not_parseable")
    if not components:
        return warnings
    for item in texts:
        if item.get("user_confirmed"):
            continue
        raw = item["text"].strip()
        if raw in {"+", "-", chr(8722)}:
            sources = [c for c in components if c.polarity]
            if not sources:
                continue
            source = min(sources, key=lambda c: math.dist(center(item["bbox"]), center(c.bbox)))
            near = min(
                range(2),
                key=lambda k: math.dist(center(item["bbox"]), source.terminals[k].xy),
            )
            if math.dist(center(item["bbox"]), source.terminals[near].xy) < max(
                40, math.dist(*[t.xy for t in source.terminals])
            ):
                source.polarity = Polarity(
                    positive_terminal=source.terminals[near if raw == "+" else 1 - near].id
                )
                item.update(
                    assigned_to=source.id,
                    outcome="assigned",
                    reason="polarity",
                    role="polarity",
                )
                item["assignments"].append(
                    {"component_id": source.id, "role": "polarity", "parsed": None}
                )
                item["association"] = {
                    "component_id": source.id,
                    "role": "polarity",
                    "parsed": None,
                }
    name_side = {}
    claimed = set()
    all_ambiguous = set()
    for role in ["name", "value", "internal", "unknown"]:
        candidates = []
        for index, item in enumerate(texts):
            if index in confirmed:
                continue
            v = item["parsed"]
            if v and (
                (
                    role == "name"
                    and v["label"]
                    and (item.get("ocr_backend") != "hybrid" or v["number"] is None)
                )
                or (role == "value" and v["number"] is not None and not v["internal"])
                or (role == "internal" and v["internal"] and v["number"] is not None)
                or (role == "unknown" and v["unknown"])
            ):
                candidates.append(index)
        if not candidates:
            continue
        costs = np.full((len(components), len(candidates) + len(components)), 1e6)
        values = {}
        for row, c in enumerate(components):
            a, b = [t.xy for t in c.terminals]
            length = max(1, math.dist(a, b))
            axis = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
            cx, cy = center(c.bbox)
            limit = max(65, (c.bbox[2] - c.bbox[0] + c.bbox[3] - c.bbox[1]) * weight * 1.5)
            costs[row, len(candidates) + row] = limit * 2
            for column, index in enumerate(candidates):
                item = texts[index]
                v = parse_item(item, "resistor" if role == "internal" else c.type)
                x, y = center(item["bbox"])
                distance = math.hypot(
                    max(c.bbox[0] - x, 0, x - c.bbox[2]),
                    max(c.bbox[1] - y, 0, y - c.bbox[3]),
                )
                min_other = min(
                    (
                        math.hypot(
                            max(other.bbox[0] - x, 0, x - other.bbox[2]),
                            max(other.bbox[1] - y, 0, y - other.bbox[3]),
                        )
                        for other in components
                        if other.id != c.id
                    ),
                    default=float("inf"),
                )
                reason = "eligible"
                hybrid = item.get("ocr_backend") == "hybrid"
                if v is None:
                    reason = "not_parseable"
                elif hybrid and item.get("ocr_conflict"):
                    reason = "ocr_conflict"
                elif hybrid and item.get("confidence", 0) < 0.65:
                    reason = "low_confidence"
                elif hybrid and v.get("label") and c.label and v["label"] != c.label:
                    reason = "identity_conflict"
                elif (
                    hybrid
                    and v.get("label")
                    and any(other.id != c.id and other.label == v["label"] for other in components)
                ):
                    reason = "identity_conflict"
                elif distance > limit:
                    reason = "too_far"
                elif min_other < distance * 0.55:
                    reason = "closer_to_other_component"
                elif not label_allowed(c, v):
                    reason = "label_type_mismatch"
                elif role == "internal" and component_unit(c.type) != "V":
                    reason = "unsupported_role"
                elif role == "value" and (
                    component_unit(c.type) is None or v["unit"] != component_unit(c.type)
                ):
                    reason = "unit_mismatch"
                elif role == "value" and not inference_supported(c, item, v, distance):
                    reason = "weak_context"
                item["candidates"].append(
                    {
                        "component_id": c.id,
                        "role": role,
                        "distance": round(distance, 2),
                        "reason": reason,
                    }
                )
                if reason != "eligible":
                    if item["outcome"] != "assigned":
                        item["reason"] = reason
                    continue
                axial = abs((x - cx) * axis[0] + (y - cy) * axis[1])
                normal = (x - cx) * (-axis[1]) + (y - cy) * axis[0]
                cost = distance * (1 + 0.7 * axial / max(1, math.hypot(x - cx, y - cy)))
                if role == "value" and c.id in name_side and normal * name_side[c.id] < 0:
                    cost *= 1.5
                if item.get("component_id"):
                    cost += -25 if item["component_id"] == c.id else limit
                costs[row, column] = cost + 10 * (1 - item.get("confidence", 0.5))
                item["candidates"][-1]["score"] = round(float(costs[row, column]), 3)
                values[row, column] = v
        # Ambiguity check
        ambiguous_candidates = set()
        for col, cand_idx in enumerate(candidates):
            col_costs = [
                (costs[r, col], components[r])
                for r in range(len(components))
                if costs[r, col] < costs[r, len(candidates) + r]
            ]
            col_costs.sort(key=lambda x: x[0])
            if (
                len(col_costs) >= 2
                and col_costs[1][0] < 1e5
                and (col_costs[1][0] - col_costs[0][0]) / max(1e-3, col_costs[0][0]) < 0.15
            ):
                cand_item = texts[cand_idx]
                cand_v = cand_item.get("parsed") or {}
                if col_costs[0][1].type == col_costs[1][1].type:
                    ambiguous_candidates.add(cand_idx)
                    all_ambiguous.add(cand_idx)
                    cand_item.update(
                        outcome="unassigned",
                        reason="ambiguous",
                        role="name_value"
                        if (cand_v.get("label") and cand_v.get("number") is not None)
                        else role,
                    )
        rows, columns = linear_sum_assignment(costs)
        for row, column in zip(rows, columns):
            if column >= len(candidates) or costs[row, column] >= costs[row, len(candidates) + row]:
                continue
            index = candidates[column]
            if index in ambiguous_candidates:
                continue
            c = components[row]
            item = texts[index]
            v = values[row, column]
            confidence = min(item.get("confidence", 0.5), v["confidence"])
            applied = True
            if role == "name":
                if not v.get("emf_symbol"):
                    c.label = v["label"]
                a, b = [t.xy for t in c.terminals]
                x, y = center(item["bbox"])
                cx, cy = center(c.bbox)
                name_side[c.id] = (x - cx) * (-(b[1] - a[1])) + (y - cy) * (b[0] - a[0])
            elif role == "internal":
                c.internal_resistance = max(0, v["number"])
            elif role == "unknown":
                if c.value.number is None:
                    c.value.confidence = confidence
            else:
                same_reading = (
                    c.value.source in {"ocr", "vlm"}
                    and c.value.number == v["number"]
                    and c.value.unit == v["unit"]
                )
                applied = (
                    c.value.source != "user"
                    and c.value.status != "user"
                    and (c.value.number is None or confidence > c.value.confidence or same_reading)
                )
                if applied:
                    if (
                        item.get("ocr_backend") == "hybrid"
                        and v.get("label")
                        and not v.get("emf_symbol")
                    ):
                        c.label = v["label"]
                    c.value = Value(
                        number=v["number"],
                        unit=v["unit"],
                        status="given",
                        source=item.get("source", "ocr"),
                        confidence=confidence,
                        unit_inferred=v.get("unit_inferred", False),
                    )
                    claimed.add(index)
                    if v.get("unit_inferred"):
                        warnings.append(("unit_inferred", c.id))
                elif c.value.source == "user" or c.value.status == "user":
                    item["reason"] = "user_value_protected"
            if applied:
                is_combined = bool(
                    v.get("label") and v.get("number") is not None and not v.get("internal")
                )
                effective_role = "combined" if is_combined else role
                item["assignments"].append(
                    {"component_id": c.id, "role": effective_role, "parsed": v}
                )
                item.update(
                    assigned_to=c.id,
                    parsed=v,
                    outcome="assigned",
                    reason="assigned",
                    role=effective_role,
                )
                item["association"] = {"component_id": c.id, "role": effective_role, "parsed": v}
    for c in components:
        if c.value.number is not None:
            continue
        eligible = []
        for index, item in enumerate(texts):
            # Hybrid candidates must pass the global solve; never bypass its
            # unit/identity/conflict/ambiguity rejections with a local rescue.
            if (
                index in confirmed
                or item.get("ocr_backend") == "hybrid"
                or index in claimed
                or index in all_ambiguous
            ):
                continue
            v = parse_item(item, c.type)
            x, y = center(item["bbox"])
            inside = any(
                a <= x <= right and b <= y <= bottom for a, b, right, bottom in search_windows(c)
            )
            distance = math.hypot(
                max(c.bbox[0] - x, 0, x - c.bbox[2]),
                max(c.bbox[1] - y, 0, y - c.bbox[3]),
            )
            if (
                inside
                and item.get("confidence", 0) >= 0.35
                and v
                and component_unit(c.type)
                and v["number"] is not None
                and not v["internal"]
                and label_allowed(c, v)
                and v["unit"] == component_unit(c.type)
                and inference_supported(c, item, v, distance)
            ):
                eligible.append((index, item, v))
        if len(eligible) == 1:
            index, item, v = eligible[0]
            c.value = Value(
                number=v["number"],
                unit=v["unit"],
                status="given",
                source="ocr",
                confidence=min(0.6, item.get("confidence", 0.5)),
                unit_inferred=True,
            )
            claimed.add(index)
            warnings.append(("unit_inferred", c.id))
            item.update(
                assigned_to=c.id,
                parsed=v,
                outcome="assigned",
                reason="anchored_rescue",
                role="value",
            )
            item["assignments"].append({"component_id": c.id, "role": "value", "parsed": v})
    return warnings
