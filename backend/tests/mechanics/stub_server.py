"""TEST-OWNED loopback app: inject fixture boxes/raw OCR, never finished scenes.

There is no production environment switch or HTTP endpoint enabling this oracle.
"""

import argparse
import hashlib
from pathlib import Path
import tempfile
import time

import uvicorn

from circuit_sim.backend.app import main
from circuit_sim.backend.domains import get
from circuit_sim.backend.domains.mechanics import corrections
from circuit_sim.backend.domains.mechanics.detect import WeightsUnavailable
from circuit_sim.backend.tests.mechanics.perception_fixtures import case, ROOT
from circuit_sim.backend.tools.mechanics.build_fixtures import fixtures


def make_app():
    sources = {}
    active = {}
    for name in fixtures():
        image, _, detector, reader = case(name)
        sources[hashlib.sha256(image.tobytes()).hexdigest()] = (detector, reader)

    def pause(check):
        for _ in range(12):
            check()
            time.sleep(0.05)

    def detector(image, check):
        pause(check)
        entry = sources.get(hashlib.sha256(image.tobytes()).hexdigest())
        if entry is None:
            raise WeightsUnavailable("TEST missing mechanics weights; author the source image.")
        active["reader"] = entry[1]
        return entry[0](image, check)

    def reader(image, **kwargs):
        pause(kwargs["check"])
        return active["reader"](image, **kwargs)

    mechanics = get("mechanics")
    mechanics.detector, mechanics.text_reader = detector, reader
    original_analyze = mechanics.analyze

    def analyze(image, options, progress):
        def report(stage, partial=None):
            progress(stage, partial)
            if stage == "geometry" and partial and partial.get("texts"):
                pause(lambda: progress(stage))

        return original_analyze(image, options, report)

    mechanics.analyze = analyze
    main.start_warmup = lambda: None  # TEST only: no real models in the oracle server
    main.model_state.update(detector="test_oracle", ocr="test_oracle")
    root = Path(tempfile.mkdtemp(prefix="m5-browser-corrections-", dir=ROOT / ".cache"))
    save = corrections.save_correction
    corrections.save_correction = lambda data, scene_json, root=None: save(
        data, scene_json, root=output_root
    )
    output_root = root
    return main.app


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8007)
    args = parser.parse_args()
    uvicorn.run(make_app(), host="127.0.0.1", port=args.port, log_level="warning")
