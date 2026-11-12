import json
from pathlib import Path
import pytest
from circuit_sim.backend.pipeline.netlist import Netlist, Constraint
from circuit_sim.backend.pipeline.resolve import resolve

F = Path(__file__).resolve().parents[2] / "fixtures"


def load(name):
    return Netlist.model_validate(json.loads((F / (name + ".json")).read_text())["netlist"])


def unknown(n, id_):
    c = next(c for c in n.components if c.id == id_)
    c.value.number = None
    c.value.status = "assumed"
    return c


def test_determined():
    n = load("single_resistor")
    unknown(n, "R1")
    n.constraints = [Constraint(type="current", target="R1", value=3)]
    out = resolve(n)
    r = out.components[1]
    assert r.value.status == "solved"
    assert r.value.number == pytest.approx(4)


def test_underdetermined_nearest_priors():
    n = load("series")
    unknown(n, "R1")
    unknown(n, "R2")
    n.constraints = [Constraint(type="current", target="R1", value=1)]
    out = resolve(n)
    assert all(c.value.status == "assumed" for c in out.components[1:])
    assert sum(c.value.number for c in out.components[1:]) == pytest.approx(12, rel=1e-6)


def test_inconsistent():
    n = load("single_resistor")
    unknown(n, "R1")
    n.constraints = [
        Constraint(type="current", target="R1", value=2),
        Constraint(type="current", target="R1", value=4),
    ]
    out = resolve(n)
    assert any(w.code == "inconsistent_constraints" for w in out.warnings)
    assert out.components[1].value.status == "assumed"


def test_all_unknown_and_user_protected():
    n = load("single_resistor")
    unknown(n, "V1")
    unknown(n, "R1")
    out = resolve(n)
    assert all(c.value.status == "assumed" for c in out.components)
    n.components[1].value.number = 7
    n.components[1].value.status = "user"
    out = resolve(n)
    assert out.components[1].value.number == 7
    assert out.components[1].value.status == "user"


def test_recompute_solved_on_user_change():
    n = load("series")
    unknown(n, "R2")
    n.constraints = [Constraint(type="current", target="R1", value=1)]
    out = resolve(n)
    assert out.components[2].value.number == pytest.approx(8)
    out.components[1].value.number = 6
    out.components[1].value.status = "user"
    out = resolve(out)
    assert out.components[2].value.number == pytest.approx(6)


def test_virtual_source():
    n = load("single_resistor")
    n.components = n.components[1:]
    out = resolve(n)
    assert out.components[-1].virtual
    assert any(w.code == "virtual_source" for w in out.warnings)
