"""Circuit-only subset of AugmentedPhysics PhysicsSymbolCandidateResolver.

Unlike its general physics table, these are review proposals, never calibrated
OCR readings. No theta/8 prior, global replacement, or invented numeric value.
"""

import re
from .normalize import normalize


class PhysicsSymbolCandidateResolver:
    def enrich(self, item):
        text = normalize(item["text"])
        proposals = []
        match = re.fullmatch(r"((?:R\d+\s*=\s*)?\d+(?:\.\d+)?)\s+([OQoq0])", text)
        if match:
            proposals.append(
                {
                    "text": match[1] + " Ω",
                    "evidence": [
                        "separate_unit_position",
                        "requires_resistance_and_visual_confirmation",
                    ],
                    "unit_inferred": True,
                }
            )
        if text in {"I", "1", "l", "E", "ε"}:
            alternatives = {
                "I": ["1", "l"],
                "1": ["I", "l"],
                "l": ["I", "1"],
                "E": ["ε"],
                "ε": ["E"],
            }
            proposals.extend(
                {"text": s, "evidence": ["ambiguous_isolated_symbol"]} for s in alternatives[text]
            )
        if re.search(r"\d\s*[uµμ][FH]$", text):
            proposals.append(
                {
                    "text": re.sub(r"[uµμ](?=[FH]$)", "μ", text),
                    "evidence": ["explicit_SI_prefix_and_unit"],
                }
            )
        if proposals:
            item["symbol_proposals"] = proposals
        return item
