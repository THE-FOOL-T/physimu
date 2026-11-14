"""Spatial mechanics label grammar. Bare names never acquire a physical unit."""

from dataclasses import dataclass, asdict
import math
import re
import unicodedata

from ...core import OCR_DIGITS

# HUMAN: Bengali unit words need native-speaker review; never a reviewed-language claim.
BN_UNITS_PENDING_REVIEW = {
    "কিলোগ্রাম": "kg",
    "কেজি": "kg",
    "গ্রাম": "g",
    "সেন্টিমিটার": "cm",
    "মিলিমিটার": "mm",
    "মিটার": "m",
    "সেকেন্ড": "s",
    "নিউটন": "N",
    "ডিগ্রি": "deg",
}
NUM = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
UNIT = r"N\s*/\s*m|m\s*/\s*s\s*(?:\^\s*2|2)|m\s*/\s*s|kg\s*/\s*s|rad\s*/\s*s|1\s*/\s*s|kg|cm|mm|deg|°|[gmN]"
PATTERN = re.compile(
    r"(?<![\w.])(?:(?P<name>[A-Za-zμµθΘω][\w]*)\s*[:=]\s*)?(?P<number>"
    + NUM
    + r")\s*(?P<unit>"
    + UNIT
    + r")?(?![\w./])"
)


def normalize(raw):
    text = unicodedata.normalize("NFC", raw or "").translate(OCR_DIGITS)
    text = text.replace("−", "-").replace("²", "^2").replace("µ", "μ").replace("٫", ".")
    text = text.replace("ₛ", "s").replace("ₖ", "k")
    for a, b in BN_UNITS_PENDING_REVIEW.items():
        text = text.replace(a, b)
    return re.sub(r"(?<=\d),(?=\d)", ".", text)


@dataclass
class Token:
    kind: str
    number: float | None
    unit: str
    name: str | None
    text: str
    bbox: list[float]
    confidence: float
    source: str = "ocr"
    conflict: bool = False

    def as_dict(self):
        return asdict(self)


def parse(raw, bbox=(0.0, 0.0, 1.0, 1.0), confidence=1.0, source="ocr"):
    text = normalize(raw).strip()
    result = []
    for match in PATTERN.finditer(text):
        n = float(match["number"])
        if not math.isfinite(n):
            continue
        name = match["name"]
        unit = re.sub(r"\s+", "", match["unit"] or "")
        kind = "unplaced"
        if unit in {"kg", "g"}:
            kind = "mass"
            n *= 0.001 if unit == "g" else 1
            unit = "kg"
        elif unit in {"m", "cm", "mm"}:
            kind = "length"
            n *= {"m": 1, "cm": 0.01, "mm": 0.001}[unit]
            unit = "m"
        elif unit in {"deg", "°"}:
            kind = "angle"
            unit = "deg"
        elif unit == "m/s":
            kind = "speed"
        elif unit == "m/s^2" or unit == "m/s2":
            kind = "acceleration" if name and name.lower() not in {"g", "gravity"} else "gravity"
            unit = "m/s^2"
        elif unit == "N/m":
            kind = "spring_constant"
        elif unit == "N":
            kind = "force"
        elif unit in {"kg/s", "1/s"}:
            kind = "damping"
        elif name and (name.startswith(("μ", "mu")) or name.lower() == "e") and not unit:
            kind = (
                "friction_static"
                if name.endswith(("s", "_s"))
                else "friction_kinetic"
                if name.startswith(("μ", "mu"))
                else "restitution"
            )
            unit = "1"
        elif unit == "rad/s":
            kind = "angular_speed"
        result.append(
            Token(
                kind,
                n,
                unit or "1",
                name,
                raw,
                list(map(float, bbox)),
                min(1.0, max(0.0, float(confidence))),
                source,
            )
        )
    if not result and re.fullmatch(r"[A-Za-zμθΘ][\w]*", text):
        result.append(
            Token("name", None, "1", text, raw, list(map(float, bbox)), float(confidence), source)
        )
    return result


def read_tokens(readings):
    result = []
    for row in readings:
        if re.match(r"^\s*Fig(?:ure)?\.?\s*\d+\b", row.get("text", ""), re.I):
            continue
        choices = [
            r for r in [row, *row.get("alternatives", [])] if r.get("binding_eligible", True)
        ]
        if not choices:
            continue
        parsed = [
            parse(
                r.get("text", ""),
                r.get("bbox", row["bbox"]),
                r.get("confidence", row.get("confidence", 0)),
                r.get("source", "ocr"),
            )
            for r in choices
        ]
        selected = max(
            parsed,
            key=lambda ts: (
                sum(t.kind not in {"unplaced", "name"} for t in ts),
                max((t.confidence for t in ts), default=0),
            ),
        )
        # Confident incompatible readings remain unresolved; engine scores are
        # not calibrated votes that can silently settle contradictory numbers.
        for token in selected:
            token.conflict = any(
                other.kind not in {"unplaced", "name"}
                and token.kind not in {"unplaced", "name"}
                and other.confidence >= 0.65
                and token.confidence >= 0.65
                and (
                    other.kind != token.kind
                    or other.unit != token.unit
                    or other.number != token.number
                )
                for candidates in parsed
                for other in candidates
            )
        result.extend(selected)
    return result
