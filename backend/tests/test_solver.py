import json
from pathlib import Path
import pytest
from circuit_sim.backend.pipeline.netlist import Netlist
from circuit_sim.backend.solver.mna import solve, transient

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


@pytest.mark.parametrize("path", sorted(FIXTURES.glob("*.json")), ids=lambda p: p.stem)
def test_analytical_fixture(path):
    f = json.loads(path.read_text())
    net = Netlist.model_validate(f["netlist"])
    out = solve(net)
    for n, value in f["expected"].get("node_voltages", {}).items():
        assert out["node_voltages"][n] == pytest.approx(value, rel=1e-6, abs=1e-12)
    for c, value in f["expected"].get("currents", {}).items():
        assert out["components"][c]["current"] == pytest.approx(value, rel=1e-6, abs=1e-12)
    if f["expected"].get("short"):
        assert out["short_circuit"]["detected"]
    for c in f["expected"].get("bypassed", []):
        assert c in out["short_circuit"]["bypassed"]
    assert out["invariants"]["max_kcl_error"] < max(
        1e-10, max(abs(c["current"]) for c in out["components"].values()) * 1e-9
    )
    assert out["invariants"]["relative_power_error"] < 1e-9
    if "transient" in f:
        t = f["transient"]
        series = transient(net, t["duration"], t["steps"])
        assert series["samples"][-1]["state"][t["component"]] == pytest.approx(t["final"], rel=1e-6)


def test_wire_flow_and_exact_path():
    f = json.loads((FIXTURES / "source_short.json").read_text())
    out = solve(Netlist.model_validate(f["netlist"]))
    assert len(out["short_circuit"]["short_paths"]) == 1
    path = out["short_circuit"]["short_paths"][0]
    assert path["segments"] and path["components"] == ["S1"]
    assert path["current"] == pytest.approx(12 / 0.051)
    assert all(abs(i) == pytest.approx(12 / 0.051) for i in out["segment_currents"].values())


def test_floating_and_conflicting_sources_are_explicit():
    f = json.loads((FIXTURES / "parallel.json").read_text())
    n = Netlist.model_validate(f["netlist"])
    n.nodes.append(type(n.nodes[0])(id="floating"))
    assert any(w["code"] == "floating_node" for w in solve(n)["warnings"])
    extra = n.components[0].model_copy(deep=True)
    extra.id = "V2"
    extra.value.number = 6
    for t in extra.terminals:
        t.id = t.id.replace("V1", "V2")
    extra.polarity.positive_terminal = "V2.a"
    n.components.append(extra)
    out = solve(n)
    assert any(w["code"] == "conflicting_sources" for w in out["warnings"])
    assert out["invariants"]["relative_power_error"] < 1e-9
