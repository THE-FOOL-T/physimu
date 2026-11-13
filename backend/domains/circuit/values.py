"""English/Bangla values and constraints in base SI units."""

import re
from ...core.value_tokens import NUM, PREFIX, UNITS, DIGITS, normalize, parse_value, component_unit


def parse_constraints(text):
    from .netlist import Constraint

    text = normalize(text or "")
    constraints = []
    patterns = [
        (
            "current",
            r"(?:I\s*\(\s*([A-Za-z]\d+)\s*\)|current\s+(?:through|in)\s+([A-Za-z]\d+)|([A-Za-z]\d+)\s+(?:এর\s+)?প্রবাহ)\s*(?:=|is|:)\s*("
            + NUM
            + r")\s*([muµ]?)A",
        ),
        (
            "voltage",
            r"(?:V\s*\(\s*([A-Za-z]\d+)\s*\)|voltage\s+(?:across|on)\s+([A-Za-z]\d+)|([A-Za-z]\d+)\s+(?:এর\s+)?বিভব)\s*(?:=|is|:)\s*("
            + NUM
            + r")\s*([m]?)V",
        ),
        (
            "power",
            r"(?:P\s*\(\s*([A-Za-z]\d+)\s*\)|power\s+(?:in|of)\s+([A-Za-z]\d+)|([A-Za-z]\d+)\s+ক্ষমতা)\s*(?:=|is|:)\s*("
            + NUM
            + r")\s*([mk]?)W",
        ),
    ]
    for kind, pattern in patterns:
        for m in re.finditer(pattern, text, re.I):
            target = next(x for x in m.groups()[:3] if x)
            constraints.append(
                Constraint(
                    type=kind,
                    target=target,
                    value=float(m[4]) * PREFIX.get(m[5], 1),
                    unit={"current": "A", "voltage": "V", "power": "W"}[kind],
                )
            )
    for m in re.finditer(r"([RCLV]\d+)\s*/\s*([RCLV]\d+)\s*=\s*(" + NUM + r")", text):
        constraints.append(Constraint(type="ratio", target=m[1] + "/" + m[2], value=float(m[3])))
    measurement = r"\s*(?:=|is|:|হয়|হয়)?\s*(" + NUM + r")\s*([pnuµμmkKMG]?)\s*"
    for kind, pattern, unit in [
        (
            "equivalent_resistance",
            r"(?:equivalent\s+resistance|Req|তুল্য\s*রোধ)",
            r"(?:Ω|Ω|ohms?)",
        ),
        ("power", r"(?:total\s+power|Ptotal|মোট\s*(?:ক্ষমতা|শক্তি))", r"W"),
        ("current", r"(?:total\s+current|Itotal|মোট\s*(?:তড়িৎ\s*)?প্রবাহ)", r"A"),
    ]:
        for m in re.finditer(pattern + measurement + unit, text, re.I):
            constraints.append(
                Constraint(
                    type=kind,
                    target="total",
                    value=float(m[1]) * PREFIX[m[2]],
                    unit={"equivalent_resistance": "ohm", "power": "W", "current": "A"}[kind],
                )
            )
    pairs = [
        r"\bV\s*([A-Z])\s*([A-Z])",
        r"(?:potential\s+difference|voltage)\s+between\s+([A-Z])\s+and\s+([A-Z])",
        r"([A-Z])\s*ও\s*([A-Z])\s*এর\s*বিভব\s*পার্থক্য",
    ]
    for pattern in pairs:
        for m in re.finditer(pattern + measurement + r"V", text, re.I):
            constraints.append(
                Constraint(
                    type="voltage",
                    target=m[1].upper() + "-" + m[2].upper(),
                    value=float(m[3]) * PREFIX[m[4]],
                    unit="V",
                )
            )
    return constraints
