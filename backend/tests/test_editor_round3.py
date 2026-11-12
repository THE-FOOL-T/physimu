import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from circuit_sim.backend.app.main import app


def test_edited_run_keeps_user_value_and_provenance():
    fixture = Path(__file__).resolve().parents[2] / "fixtures/editor_loop.json"
    net = json.loads(fixture.read_text(encoding="utf-8"))["netlist"]
    net["meta"]["provenance"] = "edited"
    response = TestClient(app).post("/api/solve", json={"netlist": net, "overrides": {"R1": 220}})
    assert response.status_code == 200
    result = response.json()
    assert result["netlist"]["version"] == 1 and result["netlist"]["meta"]["provenance"] == "edited"
    value = next(c["value"] for c in result["netlist"]["components"] if c["id"] == "R1")
    assert value["number"] == 220 and value["status"] == "user" and value["source"] == "user"
    assert result["solution"]["components"]["R1"]["current"] == pytest.approx(3 / 220)
