"""Versioned interchange contract. All coordinates are native image pixels."""

import json
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False, populate_by_name=True)


class Value(Model):
    number: float | None = None
    unit: str = "ohm"
    status: Literal["given", "solved", "assumed", "user"] = "assumed"
    source: Literal["ocr", "vlm", "constraint", "prior", "user"] = "prior"
    confidence: float = Field(default=0, ge=0, le=1)
    unit_inferred: bool = False


class Terminal(Model):
    id: str
    xy: tuple[float, float]
    node: str


class Polarity(Model):
    positive_terminal: str


class Component(Model):
    id: str
    type: str  # extensible; unknowns are retained and explicitly warned
    label: str | None = None
    bbox: tuple[float, float, float, float] = (0, 0, 0, 0)
    orientation_deg: float = 0
    terminals: list[Terminal] = Field(min_length=2, max_length=2)
    value: Value = Field(default_factory=Value)
    polarity: Polarity | None = None
    switch_closed: bool = True
    internal_resistance: float | None = Field(default=None, ge=0)
    initial_voltage: float = 0
    initial_current: float = 0
    virtual: bool = False
    confidence: float = Field(default=0, ge=0, le=1)
    disabled: bool = False


class Node(Model):
    id: str
    is_ground: bool = False
    label: str | None = None


class Point(Model):
    id: str
    xy: tuple[float, float]
    kind: Literal["junction", "terminal", "bend"] = "bend"
    node: str


class Segment(Model):
    id: str
    from_: str = Field(alias="from")
    to: str
    polyline: list[tuple[float, float]] = Field(min_length=2)
    node: str
    confidence: float = Field(default=0, ge=0, le=1)


class WireGraph(Model):
    points: list[Point] = Field(default_factory=list)
    segments: list[Segment] = Field(default_factory=list)


class Constraint(Model):
    type: Literal["current", "voltage", "power", "equivalent_resistance", "ratio"]
    target: str = Field(
        description="Component id/label; total for aggregate current/power/equivalent resistance; A-B for node-label voltage; R1/R2 for a ratio."
    )
    value: float
    unit: str = ""
    source: Literal["problem_text", "diagram"] = "problem_text"


class Warning(Model):
    code: str
    ref: str | None = None
    message_key: str


class Image(Model):
    path: str = ""
    width: int = Field(default=800, gt=0)
    height: int = Field(default=500, gt=0)


class Meta(Model):
    problem_text: str | None = None
    language: Literal["en", "bn"] = "en"
    degraded: bool = False
    style: str = "unknown"
    region: tuple[int, int, int, int] | None = None
    provenance: Literal["extracted", "partial", "demo_fallback", "edited"] = "extracted"

    @field_validator("provenance", mode="before")
    @classmethod
    def legacy_provenance(cls, value):
        return (
            "extracted"
            if value in {"automatic", "saved", "example", "synthetic exact geometry"}
            else value
        )


class Netlist(Model):
    version: Literal[1] = 1
    image: Image = Field(default_factory=Image)
    components: list[Component] = Field(default_factory=list)
    nodes: list[Node] = Field(default_factory=list)
    wire_graph: WireGraph = Field(default_factory=WireGraph)
    constraints: list[Constraint] = Field(default_factory=list)
    warnings: list[Warning] = Field(default_factory=list)
    meta: Meta = Field(default_factory=Meta)

    @model_validator(mode="after")
    def references(self):
        for items in [
            self.components,
            self.nodes,
            self.wire_graph.points,
            self.wire_graph.segments,
        ]:
            ids = [i.id for i in items]
            if len(ids) != len(set(ids)):
                raise ValueError("Duplicate ids")
        nodes = {n.id for n in self.nodes}
        points = {p.id: p for p in self.wire_graph.points}
        terminal_ids = [t.id for c in self.components for t in c.terminals]
        if len(terminal_ids) != len(set(terminal_ids)):
            raise ValueError("Duplicate terminal ids")
        for c in self.components:
            if any(t.node not in nodes for t in c.terminals):
                raise ValueError(f"Unknown node on {c.id}")
            if c.polarity and c.polarity.positive_terminal not in {t.id for t in c.terminals}:
                raise ValueError(f"Invalid polarity on {c.id}")
        for p in points.values():
            if p.node not in nodes:
                raise ValueError(f"Unknown node on {p.id}")
        for s in self.wire_graph.segments:
            if s.from_ not in points or s.to not in points:
                raise ValueError(f"Unknown wire point on {s.id}")
            if s.node not in nodes or points[s.from_].node != s.node or points[s.to].node != s.node:
                raise ValueError(f"Wire crosses electrical nodes: {s.id}; merge nodes first")
        return self

    def warn(self, code, ref=None):
        if not any(w.code == code and w.ref == ref for w in self.warnings):
            self.warnings.append(Warning(code=code, ref=ref, message_key="warn." + code))

    def as_dict(self):
        return self.model_dump(mode="json", by_alias=True)


def load(path: str | Path) -> Netlist:
    return Netlist.model_validate_json(Path(path).read_text(encoding="utf-8"))


def save(netlist: Netlist, path):
    Path(path).write_text(
        json.dumps(netlist.as_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
