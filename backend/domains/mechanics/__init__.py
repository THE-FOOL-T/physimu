"""Mechanics perception plugin. Solving stays in the browser."""


class MechanicsDomain:
    name = "mechanics"
    stages = (
        "received",
        "preprocess",
        "detect",
        "text",
        "geometry",
        "associate",
        "archetype",
        "validate",
        "done",
    )

    def __init__(self, detector=None, text_reader=None):
        self.detector, self.text_reader = detector, text_reader

    def analyze(self, image, options: dict, progress=None) -> dict:
        from .engine import analyze_mechanics_page

        return analyze_mechanics_page(
            image, options, progress, detector=self.detector, text_reader=self.text_reader
        )
