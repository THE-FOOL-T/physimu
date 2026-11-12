"""Version-one mechanics document. No extraction or physics runs in this module."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .defaults import assumed, scene_defaults

Number = Annotated[float, Field(strict=True, allow_inf_nan=False)]
Point = tuple[Number, Number]
BBox = tuple[Number, Number, Number, Number]
Archetype = Literal[
    "projectile",
    "incline_block",
    "pendulum",
    "spring_mass",
    "atwood",
    "table_pulley",
    "incline_pulley",
    "collision_1d",
    "unsupported",
]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", json_schema_serialization_defaults_required=True)


class Value(Strict):
    number: Number | None
    unit: str
    status: Literal["given", "solved", "assumed", "user"]
    source: Literal["ocr", "vlm", "geometry", "constraint", "prior", "user"]
    confidence: Annotated[Number, Field(ge=0, le=1)]


def prior(name: str) -> Value:
    return Value(**assumed(name))


class Vector(Strict):
    x: Value
    y: Value


class Initial(Strict):
    position: Vector
    velocity: Vector


class Image(Strict):
    path: str
    width: Annotated[int, Field(strict=True, gt=0)]
    height: Annotated[int, Field(strict=True, gt=0)]


class Frame(Strict):
    gravity: Point = (0.0, 1.0)
    px_per_m: Value
    paper_color: Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}$")] = "#fffef7"
    ink_color: Annotated[str, Field(pattern=r"^#[0-9a-fA-F]{6}$")] = "#202c3a"
    stroke_px: Annotated[Number, Field(gt=0)] = 2.0


class Body(Strict):
    id: str
    type: str
    bbox: BBox
    mask: Annotated[list[Point], Field(min_length=3)]
    anchor: Point
    label_ids: list[str] = Field(default_factory=list)
    mass: Value = Field(default_factory=lambda: prior("mass"))
    radius_m: Value | None = None
    on_surface: str | None = None
    initial: Initial


class Surface(Strict):
    id: str
    type: str
    polyline: Annotated[list[Point], Field(min_length=2)]
    angle_deg: Value | None = None
    length_m: Value | None = None
    mu_s: Value = Field(default_factory=lambda: prior("mu"))
    mu_k: Value = Field(default_factory=lambda: prior("mu"))


class Endpoint(Strict):
    ref: str
    point: Point


class Link(Strict):
    id: str
    type: str
    a: Endpoint
    b: Endpoint
    polyline: Annotated[list[Point], Field(min_length=2)]
    length_m: Value | None = None
    k: Value | None = None
    rest_length_m: Value | None = None
    coils: Annotated[int, Field(strict=True, gt=0)] | None = None
    damping: Value | None = None


class Pulley(Strict):
    id: str
    center: Point
    radius_px: Annotated[Number, Field(gt=0)]
    mass: Value | None = None


class Force(Strict):
    id: str
    body: str
    tail: Point
    head: Point
    magnitude: Value | None = None
    label: str


class Geometry(Strict):
    points: list[Point] = Field(default_factory=list)
    bbox: BBox | None = None
    text: str | None = None
    radius_px: Number | None = None
    start_deg: Number | None = None
    end_deg: Number | None = None


class Annotation(Strict):
    id: str
    type: str
    geometry: Geometry
    text_id: str | None = None
    bound_to: str | None = None


class Repair(Strict):
    surface_or_line_id: str
    segments: list[Annotated[list[Point], Field(min_length=2)]]


class Control(Strict):
    min: Number
    max: Number
    step: Annotated[Number, Field(gt=0)]
    unit: str
    locked: Annotated[bool, Field(strict=True)] = False


class Binding(Strict):
    id: str
    path: str
    kind: Literal["physics", "initial", "geometry"] = Field(alias="class")
    control: Control
    labels: list[str] = Field(default_factory=list)
    handle: str | None = None
    drives: list[Literal["layout", "solver", "label"]] = Field(
        default_factory=lambda: ["layout", "solver", "label"]
    )


class Constraint(Strict):
    type: str
    refs: list[str] = Field(default_factory=list)
    values: dict[str, Value] = Field(default_factory=dict)


class Warning(Strict):
    code: str
    ref: str | None = None
    message_key: str


class Meta(Strict):
    language: Literal["en", "bn"] = "en"
    style: Literal["printed", "handwritten", "photo", "unknown"] = "unknown"
    provenance: Literal["extracted", "partial", "authored", "unsupported", "demo_fallback"]
    region: BBox | None = None


class Constants(Strict):
    g: Value = Field(default_factory=lambda: prior("g"))


def resolve_path(scene: "Scene", path: str):
    current = scene
    for part in path.split("."):
        if isinstance(current, list):
            current = next((item for item in current if getattr(item, "id", None) == part), None)
        elif isinstance(current, dict):
            current = current.get(part)
        else:
            current = getattr(current, part, None)
        if current is None:
            raise ValueError(f"unresolved path: {path}")
    return current


class Scene(Strict):
    version: Literal[1] = 1
    domain: Literal["mechanics"] = "mechanics"
    image: Image
    archetype: Archetype
    frame: Frame
    bodies: list[Body] = Field(default_factory=list)
    surfaces: list[Surface] = Field(default_factory=list)
    links: list[Link] = Field(default_factory=list)
    pulleys: list[Pulley] = Field(default_factory=list)
    forces: list[Force] = Field(default_factory=list)
    annotations: list[Annotation] = Field(default_factory=list)
    repairs: list[Repair] = Field(default_factory=list)
    constants: Constants = Field(default_factory=Constants)
    params: dict[str, Value] = Field(default_factory=dict)
    bindings: list[Binding] = Field(default_factory=list)
    constraints: list[Constraint] = Field(default_factory=list)
    warnings: list[Warning] = Field(default_factory=list)
    meta: Meta

    @model_validator(mode="before")
    @classmethod
    def defaults(cls, document):
        if isinstance(document, dict):
            if "version" in document and type(document["version"]) is not int:
                raise ValueError("version must be integer 1")
            try:
                return scene_defaults(document)
            except (TypeError, KeyError, AttributeError, OverflowError) as error:
                raise ValueError("invalid default context") from error
        return document

    @model_validator(mode="after")
    def references(self):
        groups = [
            self.bodies,
            self.surfaces,
            self.links,
            self.pulleys,
            self.forces,
            self.annotations,
        ]
        items = [item for group in groups for item in group]
        ids = {item.id for item in items}
        if any(not item.id for item in items) or len(ids) != len(items):
            raise ValueError("object ids must be nonempty and globally unique")
        annotation_ids = {item.id for item in self.annotations}
        surface_ids = {item.id for item in self.surfaces}
        body_ids = {item.id for item in self.bodies}

        def unit(value, expected):
            if value is not None and value.unit != expected:
                raise ValueError(f"expected SI unit {expected}, got {value.unit}")

        unit(self.frame.px_per_m, "px/m")
        unit(self.constants.g, "m/s^2")
        for body in self.bodies:
            unit(body.mass, "kg")
            unit(body.radius_m, "m")
            for v in (body.initial.position.x, body.initial.position.y):
                unit(v, "m")
            for v in (body.initial.velocity.x, body.initial.velocity.y):
                unit(v, "m/s")
        for surface in self.surfaces:
            unit(surface.angle_deg, "deg")
            unit(surface.length_m, "m")
            unit(surface.mu_s, "1")
            unit(surface.mu_k, "1")
        for link in self.links:
            unit(link.length_m, "m")
            unit(link.rest_length_m, "m")
            unit(link.k, "N/m")
            unit(link.damping, "1/s" if self.archetype == "pendulum" else "kg/s")
        for pulley in self.pulleys:
            unit(pulley.mass, "kg")
        for force in self.forces:
            unit(force.magnitude, "N")
        parameter_units = {
            "launch_speed": "m/s",
            "launch_angle": "deg",
            "launch_height": "m",
            "start_position": "m",
            "initial_speed": "m/s",
            "applied_force": "N",
            "release_angle": "deg",
            "angular_speed": "rad/s",
            "initial_stretch": "m",
            "vertical": "1",
            "restitution": "1",
        }
        for key, value in self.params.items():
            if key in parameter_units:
                unit(value, parameter_units[key])

        def require(ref, allowed=ids):
            if ref is not None and ref not in allowed:
                raise ValueError(f"unresolved reference: {ref}")

        known = [
            (self.bodies, {"block", "ball", "bob", "cart"}),
            (self.surfaces, {"incline", "floor", "wall", "ceiling"}),
            (self.links, {"rope", "rod", "spring"}),
            (self.annotations, {"dimension", "angle_arc", "label", "axis"}),
        ]
        for group, types in known:
            for item in group:
                if item.type not in types and not any(
                    w.code == "unknown_type" and w.ref == item.id for w in self.warnings
                ):
                    self.warnings.append(
                        Warning(code="unknown_type", ref=item.id, message_key="mech.unknown_type")
                    )
        for body in self.bodies:
            require(body.on_surface, surface_ids)
            for label in body.label_ids:
                require(label, annotation_ids)
            x0, y0, x1, y1 = body.bbox
            if x0 >= x1 or y0 >= y1:
                raise ValueError("bbox must have positive area")
        for link in self.links:
            require(link.a.ref)
            require(link.b.ref)
        for force in self.forces:
            require(force.body, body_ids)
        for annotation in self.annotations:
            require(annotation.text_id, annotation_ids)
            if annotation.bound_to:
                resolve_path(self, annotation.bound_to)
        for repair in self.repairs:
            require(repair.surface_or_line_id)
        for constraint in self.constraints:
            for ref in constraint.refs:
                require(ref)
            if constraint.type == "after_velocity":
                for ref, value in constraint.values.items():
                    require(ref, body_ids)
                    unit(value, "m/s")
        for warning in self.warnings:
            require(warning.ref)
        if len({b.id for b in self.bindings}) != len(self.bindings):
            raise ValueError("binding ids must be unique")
        for binding in self.bindings:
            value = resolve_path(self, binding.path)
            if not isinstance(value, Value):
                raise ValueError("binding must address a Value")
            c = binding.control
            if c.min >= c.max or c.unit != value.unit:
                raise ValueError("invalid control range/unit")
            if binding.kind == "geometry" and not c.locked:
                raise ValueError("authored geometry controls must start locked")
            for label in binding.labels:
                require(label, annotation_ids)
        if self.frame.px_per_m.number is not None and self.frame.px_per_m.number <= 0:
            raise ValueError("scale must be positive")
        return self
