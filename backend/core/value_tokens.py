"""Evidence-preserving OCR value parsing; ambiguous units require component context."""

import re
import unicodedata

DIGITS = str.maketrans(
    "\u09e6\u09e7\u09e8\u09e9\u09ea\u09eb\u09ec\u09ed\u09ee\u09ef"
    "\u2080\u2081\u2082\u2083\u2084\u2085\u2086\u2087\u2088\u2089",
    "01234567890123456789",
)
NUM = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
PREFIX = {
    "p": 1e-12,
    "n": 1e-9,
    "u": 1e-6,
    "µ": 1e-6,
    "μ": 1e-6,
    "m": 1e-3,
    "k": 1e3,
    "K": 1e3,
    "M": 1e6,
    "G": 1e9,
    "": 1,
}
# U+2126 OHM SIGN canonically normalizes to U+03A9 GREEK CAPITAL OMEGA.
UNITS = {
    "\u03a9": "ohm",
    "\u2126": "ohm",
    "\u03c9": "ohm",
    "ohm": "ohm",
    "ohms": "ohm",
    "v": "V",
    "volt": "V",
    "volts": "V",
    "a": "A",
    "amp": "A",
    "amps": "A",
    "f": "F",
    "farad": "F",
    "farads": "F",
    "h": "H",
    "henry": "H",
    "w": "W",
    "watt": "W",
    "watts": "W",
}
# Bengali YA+NUKTA and YYA spellings are canonically equivalent under NFC.
BN_UNITS = [
    ("\u0993\u09b9\u09ae", "Ω"),
    ("\u0993\u09ae", "Ω"),
    ("\u09ad\u09cb\u09b2\u09cd\u099f", "V"),
    ("\u0985\u09cd\u09af\u09be\u09ae\u09cd\u09aa\u09bf\u09af\u09bc\u09be\u09b0", "A"),
    ("\u0985\u09cd\u09af\u09be\u09ae\u09cd\u09aa\u09bf\u09df\u09be\u09b0", "A"),
    ("\u09ab\u09cd\u09af\u09be\u09b0\u09be\u09a1", "F"),
    ("\u09b9\u09c7\u09a8\u09b0\u09bf", "H"),
    ("\u0993\u09af\u09bc\u09be\u099f", "W"),
    ("\u0993\u09df\u09be\u099f", "W"),
]
BN_PREFIXES = [
    ("\u09ae\u09bf\u09b2\u09bf", "m"),
    ("\u09ae\u09be\u0987\u0995\u09cd\u09b0\u09cb", "u"),
    ("\u0995\u09bf\u09b2\u09cb", "k"),
    ("\u09ae\u09c7\u0997\u09be", "M"),
    ("\u09a8\u09cd\u09af\u09be\u09a8\u09cb", "n"),
    ("\u09aa\u09bf\u0995\u09cb", "p"),
]
FAMILIES = {
    "resistor": "ohm",
    "rheostat": "ohm",
    "lamp": "ohm",
    "fuse": "ohm",
    "dc_source": "V",
    "battery": "V",
    "ac_source": "V",
    "voltage_source": "V",
    "capacitor": "F",
    "inductor": "H",
    "current_source": "A",
}
CONFUSABLE_DIGITS = str.maketrans({"O": "0", "o": "0", "l": "1", "I": "1", "S": "5", "B": "8"})
TOKEN = r"[+-]?(?:[\dOoIlSB]+(?:[.,][\dOoIlSB]*)?|[.,][\dOoIlSB]+)(?:[eE][+-]?\d+)?"
UNIT_PATTERN = r"(?:ohms?\b|volts?\b|amps?\b|farads?\b|henry\b|watts?\b|[ΩΩVAFHW])"


def component_unit(context):
    return FAMILIES.get(context, context if context in {"ohm", "V", "A", "F", "H"} else None)


def normalize(text):
    text = unicodedata.normalize("NFC", text or "").translate(DIGITS)
    text = text.replace("_", "").replace("−", "-").replace("٫", ".")
    for alias, unit in dict((unicodedata.normalize("NFC", a), b) for a, b in BN_UNITS).items():
        text = text.replace(alias, unit)
    for word, prefix in BN_PREFIXES:
        text = re.sub(word + r"\s*(?=[ΩVAFHW])", prefix, text)
    text = re.sub(r"(?<=\d),(?=\d)", ".", text)
    # Hyphen/dash separator between designator and value: 'R2-3Q' -> 'R2 = 3Q'
    text = re.sub(r"([RCLVE]\s*\d+)\s*[-–—]\s*(?=\d)", r"\1 = ", text)
    # Subscript OCR confusions on resistor designator (e.g. Rz -> R3, Ri/Ru -> R1, Rs -> R3, Ry -> R)
    text = re.sub(r"\bR[zZsS]\s*(?=[-=\s])", "R3 ", text)
    text = re.sub(r"\bR[iIl|uU]\s*(?=[-=\s])", "R1 ", text)
    text = re.sub(r"\bRy\s*(?=[-=\s])", "R ", text)
    # Existing k-ohm OCR convention:
    text = re.sub(r"(?<=\d)\s*([kK])\s*[oOQn](?![A-Za-z])", r"\1Ω", text)
    # Resistor designation R... = with confusable ohm lookalikes:
    text = re.sub(r"(R\s*\d+\s*=\s*\d+(?:\.\d+)?)\s*[oOQq](?![A-Za-z])", r"\1 Ω", text)
    text = re.sub(r"(R\s*\d+\s*=\s*\d+(?:\.\d+)?)\s+9(?!\d)", r"\1 Ω", text)
    # Trailing ohm glyphs glued to numbers after resistor designation R... =
    text = re.sub(r"(R\s*\d+\s*=\s*\d+?)(?:92|Ω|Ω)(?![A-Za-z0-9])", r"\1 Ω", text)
    text = re.sub(r"(R\s*\d+\s*=\s*[1-9])2(?![A-Za-z0-9])", r"\1 Ω", text)
    text = re.sub(r"(R\s*\d+\s*=\s*[1-9])([59sSQq])(?![A-Za-z0-9])", r"\1 Ω", text)
    text = re.sub(r"(R\s*\d+\s*=\s*\d+(?:\.\d+)?)\s*$", r"\1 Ω", text)
    return text


def parse_value(raw, context=None):
    text = normalize(raw).strip()
    expected = component_unit(context)
    name = re.search(r"(?<![A-Za-z])(?:[RCLVEIKSG]\s*\d+|[RCLVE]\s*[xX]|ε|E)(?![A-Za-z])", text)
    label = re.sub(r"\s+", "", name[0]) if name else None
    if not expected and label:
        if label[0] == "R":
            expected = "ohm"
        elif label[0] in ("V", "E") or label in ("E", "ε"):
            expected = "V"
        elif label[0] == "C":
            expected = "F"
        elif label[0] == "L":
            expected = "H"
    emf = label in {"E", "ε"}
    if name:
        text = text[: name.start()] + " " + text[name.end() :]
    internal = bool(re.search(r"\binternal\s+resistance\b|\br\s*=", text, re.I))
    unknown = bool(
        re.search(
            r"\?|\bfind\b|\bdetermine\b|\bunknown\b|\bx\b|নির্ণয়|নির্ণয়|বের কর|কত",
            text,
            re.I,
        )
    )
    inferred = False
    edits = []
    if expected:
        suffix = (
            r"(?:Q|O|0|2|9|52|S2|n)" if expected == "ohm" else r"U" if expected == "V" else r"(?!)"
        )
        match = re.fullmatch(r"\s*(" + TOKEN + r")\s+" + suffix + r"\s*", text)
        if match:
            text = match[1] + " " + ("Ω" if expected == "ohm" else expected)
            inferred = True
            edits.append("contextual_unit_lookalike")
    text = re.sub(r"(?<=\d)\s+(?=\d)", "", text)
    match = re.search(
        r"(?<![A-Za-z\d])(" + TOKEN + r")\s*([pnuµμmkKMG]?)\s*(" + UNIT_PATTERN + r")",
        text,
        re.I,
    )
    unit = None
    prefix = ""
    token = None
    if match:
        token, prefix = match[1], match[2]
        unit = UNITS.get(match[3].lower())
    else:
        bare = re.fullmatch(
            r"\s*(?:=|:)?\s*(" + TOKEN + r")\s*([pnuµμmkKMG]?)\s*(?:[QOU]|S2)?\s*", text
        )
        if bare:
            token, prefix = bare[1], bare[2]
            if expected:
                unit = expected
                inferred = True
                edits.append("component_unit")
    if token and any(c.isdigit() for c in token):
        fixed = token.translate(CONFUSABLE_DIGITS).replace(",", ".")
        if fixed != token:
            edits.append("numeric_lookalike")
        try:
            number = float(fixed) * PREFIX.get(prefix, PREFIX.get(prefix.lower(), 1))
        except ValueError:
            return None
        if inferred and unit == "F" and not prefix:
            number *= 1e-6
            edits.append("bare_capacitor_microfarads")
        return {
            "label": label,
            "number": number,
            "unit": unit,
            "internal": internal,
            "unknown": False,
            "has_prefix": bool(prefix),
            "unit_inferred": inferred,
            "confidence": min(
                0.55 if unit is None else 0.6 if inferred else 0.85,
                0.7 if edits else 0.85,
            ),
            "emf_symbol": emf,
            "normalized": text.strip(),
            "normalizations": edits,
        }
    if label or unknown:
        return {
            "label": label,
            "number": None,
            "unit": None,
            "confidence": 0.6,
            "internal": internal,
            "unknown": unknown,
            "emf_symbol": emf,
            "unit_inferred": False,
            "normalized": text.strip(),
            "normalizations": edits,
        }
    return None
