"""One published mechanics execution contract for jobs and the image pipeline."""

STAGES = (
    "received",
    "preprocess",
    "understand",
    "detect",
    "text",
    "geometry",
    "associate",
    "archetype",
    "validate",
    "done",
)
