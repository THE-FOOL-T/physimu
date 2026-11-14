"""The optional panel field affects mechanics requests only."""

from types import SimpleNamespace

import cv2
from fastapi.testclient import TestClient
import numpy as np

from circuit_sim.backend.app import main
from circuit_sim.backend.domains.mechanics.engine import STAGES


def test_native_panel_option_is_request_local_and_circuit_ignores_it(monkeypatch):
    observed = []
    domains = {}
    for name in ("mechanics", "circuit"):

        def analyze(image, options, progress, name=name):
            observed.append((name, dict(options)))
            return {"domain": name, "region": options.get("figure_region")}

        domains[name] = SimpleNamespace(name=name, stages=STAGES, analyze=analyze)
    monkeypatch.setattr(main, "get_domain", lambda name: domains[name])
    monkeypatch.setattr(main, "check_rate", lambda request: None)
    monkeypatch.setattr(
        main,
        "run_analysis",
        lambda image, *a, domain, progress, **k: domain.analyze(image, {}, progress),
    )
    ok, raster = cv2.imencode(".png", np.full((80, 100, 3), 255, np.uint8))
    assert ok
    client = TestClient(main.app)

    def send(domain, region=None, candidate=None):
        form = {"domain": domain}
        if region is not None:
            form["figure_region"] = region
        if candidate is not None:
            form["pendulum_candidate"] = candidate
        return client.post(
            "/api/analyze", data=form, files={"image": ("TEST.png", raster.tobytes(), "image/png")}
        )

    result = send("mechanics", "[50,0,100,80]")
    assert result.status_code == 200 and result.json()["region"] == [50, 0, 100, 80]
    result = send("mechanics")
    assert result.status_code == 200 and result.json()["region"] is None
    result = send("circuit", "not a mechanics region")
    assert result.status_code == 200 and result.json() == {"domain": "circuit", "region": None}
    assert send("mechanics", candidate="1").status_code == 200
    assert observed[-1][1]["pendulum_candidate"] == 1
    assert send("mechanics").status_code == 200
    assert "pendulum_candidate" not in observed[-1][1]
    assert send("circuit", candidate="not a mechanics candidate").status_code == 200
    assert "pendulum_candidate" not in observed[-1][1]
    count = len(observed)
    assert send("mechanics", "[-1,0,100,80]").status_code == 422
    assert send("mechanics", "not JSON").status_code == 422
    assert send("mechanics", candidate="-1").status_code == 422
    assert send("mechanics", candidate="1.5").status_code == 422
    assert len(observed) == count
