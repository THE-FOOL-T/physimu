"""Strict hybrid interpretations, without the legacy parser's value priors."""

import math
import re
import unicodedata

from ..value_tokens import BN_PREFIXES, BN_UNITS, DIGITS, PREFIX, UNITS

NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
NAME = r"(?:[RCLVEIKSG]\d+|[RCLVE]x|E|ε)"
UNIT = r"(?:ohms?|volts?|amps?|farads?|henry|watts?|[ΩωVvAaFfHhWw])"


def normalize(text):
    text = unicodedata.normalize("NFC", text).translate(DIGITS)
    text = text.replace("−", "-").replace("٫", ".").replace("_", "")
    for word, unit in BN_UNITS:
        text = text.replace(unicodedata.normalize("NFC", word), unit)
    for word, prefix in BN_PREFIXES:
        text = re.sub(word + r"\s*(?=[ΩVAFHW])", prefix, text)
    text = re.sub(r"(?<=\d),(?=\d)", ".", text)
    # Only an explicit numeric SI prefix position licenses u/µ/μ equivalence.
    text = re.sub(r"(?<=\d)\s*[uµμ](?=[FHAVΩ])", " µ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse(text, context=None):
    """Parse a complete label, never a number extracted from textbook prose.

    Context deliberately cannot supply a missing unit or turn a digit into Ω.
    All fields match the association layer's existing parsed-value contract.
    """
    original = text
    text = normalize(text)
    edits = ["unicode_or_unit_alias"] if text != original.strip() else []
    label = None
    internal = False
    voltage = re.match(r"^V\s*=\s*", text)
    if voltage:
        text = text[voltage.end() :]
    name = re.match(r"^(" + NAME + r")(?![A-Za-z\d])\s*", text)
    if name:
        label = name[1]
        text = text[name.end() :].lstrip("=: ")
    else:
        resistance = re.match(r"^(?:internal resistance\s*|r\s*=\s*)", text, re.I)
        if resistance:
            internal = True
            text = text[resistance.end() :]
    unknown = text == "?"
    match = re.fullmatch(r"(" + NUMBER + r")\s*([pnuµμmkKMG]?)\s*(" + UNIT + r")?", text)
    number, unit, prefix = None, None, ""
    if match:
        prefix = match[2]
        unit = UNITS.get((match[3] or "").lower())
        number = float(match[1]) * PREFIX[prefix]
        if not math.isfinite(number):
            return None
    elif text and not unknown:
        return None
    if number is None and not label and not unknown:
        return None
    if voltage and (
        number is None
        or label is not None
        or unit != "V"
        or (context is not None and context not in {"dc_source", "voltage_source", "battery"})
    ):
        return None
    return {
        "label": label,
        "number": number,
        "unit": unit,
        "internal": internal,
        "unknown": unknown,
        "has_prefix": bool(prefix),
        "unit_inferred": False,
        "confidence": 0.85 if unit else 0.6,
        "emf_symbol": label in {"E", "ε"},
        "normalized": normalize((label + " = " if label else "") + text),
        "normalizations": edits,
    }


def explicit(item):
    value = parse(item["text"])
    return bool(value and value["number"] is not None and value["unit"])


def record(text, polygon, confidence, engine, *, rotation=0, **metadata):
    """Keep original evidence and a tight native-coordinate polygon and box."""
    points = [[float(x), float(y)] for x, y in polygon]
    confidence = float(confidence) if confidence is not None else 0.0
    if not points or not math.isfinite(confidence) or not 0 <= confidence <= 1:
        raise ValueError("Invalid OCR confidence or polygon")
    if not all(math.isfinite(v) for p in points for v in p):
        raise ValueError("Nonfinite OCR coordinates")
    xs, ys = zip(*points)
    if max(xs) <= min(xs) or max(ys) <= min(ys):
        raise ValueError("Empty OCR box")
    return {
        "text": text,
        "raw_text": text,
        "normalized_text": normalize(text),
        "bbox": [min(xs), min(ys), max(xs), max(ys)],
        "polygon": points,
        "confidence": confidence,
        "engine": engine,
        "source": "ocr",
        "rotation": rotation,
        "ocr_backend": "hybrid",
        **metadata,
    }


def to_native(points, width, height, rotation=0, offset=(0, 0)):
    """Inverse clockwise crop rotation in continuous image-edge coordinates."""
    result = []
    for x, y in points:
        if rotation == 90:
            x, y = y, height - x
        elif rotation == 180:
            x, y = width - x, height - y
        elif rotation == 270:
            x, y = width - y, x
        elif rotation != 0:
            raise ValueError("Only quarter turns are supported")
        result.append([max(0, min(width, x)) + offset[0], max(0, min(height, y)) + offset[1]])
    return result
