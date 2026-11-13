"""Call the copied circuit pipeline directly, preserving every existing result key."""

from ...core import STAGES
from .engine import analyze_page


class CircuitDomain:
    name = "circuit"
    stages = STAGES

    def __init__(self, analyzer=None):
        # The legacy service can supply its analysis hook without moving code.
        self._analyzer = analyzer

    def analyze(self, image, options: dict, progress=None) -> dict:
        result = (self._analyzer or analyze_page)(
            image,
            options.get("problem_text"),
            options.get("lang", "en"),
            options.get("style", "auto"),
            progress=progress,
            use_label_reader=options.get("use_label_reader", False),
        )
        return {**result, "domain": self.name}
