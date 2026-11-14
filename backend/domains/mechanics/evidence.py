"""Typed, diagnostic-only evidence graph. Scene v1 remains the portable contract.

Scores describe geometric/rule support, not calibrated recognition accuracy.
Unresolved relationships are retained rather than upgraded to observations.
"""

import math
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .associate import distance


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Relation(Record):
    type: Literal[
        "SUPPORTED_BY",
        "ATTACHED_TO",
        "PASSES_OVER",
        "CONNECTED_TO",
        "LABEL_OF",
        "CONSTRAINED_TO",
        "ALTERNATE_STATE_OF",
    ]
    source: str
    target: str
    confidence: float = Field(ge=0, le=1)
    evidence: list[str]
    state: Literal["candidate", "supported", "assumed", "unresolved"]


class Hypothesis(Record):
    archetype: str
    confidence: float = Field(ge=0, le=1)
    supporting: list[str]
    contradictions: list[str]
    score: float


class ObjectEvidence(Record):
    id: str
    detection_id: str | None
    type: str
    measurement: dict


class Evidence(Record):
    version: Literal[1] = 1
    coordinate_system: Literal["native_image_pixels_x_right_y_down"] = (
        "native_image_pixels_x_right_y_down"
    )
    image: dict
    recognition: dict = Field(default_factory=dict)
    figure_regions: list[list[float]] = Field(default_factory=list)
    selected_region: list[float] | None = None
    detections: list[dict] = Field(default_factory=list)
    objects: list[ObjectEvidence] = Field(default_factory=list)
    ocr: list[dict] = Field(default_factory=list)
    relationships: list[Relation] = Field(default_factory=list)
    hypotheses: list[Hypothesis] = Field(default_factory=list)
    assignments: list[dict] = Field(default_factory=list)
    unassigned_labels: list[dict] = Field(default_factory=list)
    unresolved_attachments: list[str] = Field(default_factory=list)
    assumptions: list[dict] = Field(default_factory=list)
    warnings: list[dict] = Field(default_factory=list)


def relationships(scene):
    edges = []

    def edge(type_, source, target, confidence, evidence, state="supported"):
        edges.append(
            Relation(
                type=type_,
                source=source,
                target=target,
                confidence=confidence,
                evidence=evidence,
                state=state,
            )
        )

    for body in scene["bodies"]:
        candidates = []
        for sf in scene["surfaces"]:
            if sf["type"] not in {"floor", "incline"}:
                continue
            residual = min(distance(p, sf["polyline"]) for p in body["mask"])
            if residual <= 12:
                candidates.append((sf, residual))
        for sf, residual in candidates:
            edge(
                "SUPPORTED_BY",
                body["id"],
                sf["id"],
                max(0.0, 0.95 - residual / 24),
                [f"mask_to_surface_distance_px={residual:.3f}"],
                "supported"
                if body.get("on_surface") == sf["id"] and len(candidates) == 1
                else "candidate",
            )
    objects = {
        o["id"]: o
        for group in (scene["bodies"], scene["annotations"], scene["surfaces"], scene["pulleys"])
        for o in group
    }
    for link in scene["links"]:
        for end in ("a", "b"):
            endpoint = link[end]
            obj = objects.get(endpoint["ref"])
            gap = float("inf")
            if obj:
                if "mask" in obj:
                    gap = distance(endpoint["point"], [*obj["mask"], obj["mask"][0]])
                    gap = min(gap, math.dist(endpoint["point"], obj["anchor"]))
                elif obj.get("geometry", {}).get("points"):
                    gap = min(math.dist(endpoint["point"], p) for p in obj["geometry"]["points"])
                elif "polyline" in obj:
                    gap = distance(endpoint["point"], obj["polyline"])
            state = "supported" if gap <= 12 else "unresolved"
            edge(
                "CONNECTED_TO" if link["type"] == "spring" else "ATTACHED_TO",
                f"{link['id']}.{end}",
                endpoint["ref"],
                max(0.0, 0.9 - gap / 120),
                [f"endpoint_gap_px={gap:.3f}"],
                state,
            )
        if link["type"] == "rope":
            for pulley in scene["pulleys"]:
                gap = min(
                    abs(math.dist(p, pulley["center"]) - pulley["radius_px"])
                    for p in link["polyline"]
                )
                assumed = any(
                    w["code"] == "rope_route_assumed" and w["ref"] == link["id"]
                    for w in scene["warnings"]
                )
                edge(
                    "PASSES_OVER",
                    link["id"],
                    pulley["id"],
                    0.35 if assumed else max(0.0, 0.9 - gap / 40),
                    ["inferred_wrap" if assumed else f"measured_rim_gap_px={gap:.3f}"],
                    "assumed" if assumed else "supported" if gap <= 8 else "unresolved",
                )
    for a in scene["annotations"]:
        for link in scene["links"]:
            if a["id"].startswith(f"alternate_state_{link['id']}_"):
                edge(
                    "ALTERNATE_STATE_OF",
                    a["id"],
                    link["id"],
                    0.6,
                    [
                        "measured_similar_radius_and_size",
                        "alternate_pose_interpretation_requires_review",
                    ],
                    "assumed",
                )
        if a.get("bound_to"):
            edge("LABEL_OF", a["id"], a["bound_to"], 0.8, ["typed_parameter_assignment"])
    return edges


def build_evidence(scene, diagnostics):
    fits = diagnostics.get("measurements", {})
    assumptions = []

    def visit(v, path=""):
        if isinstance(v, dict):
            if "number" in v and "status" in v:
                if v["status"] == "assumed":
                    assumptions.append(dict(path=path, **v))
            else:
                for k, child in v.items():
                    visit(child, f"{path}.{k}" if path else k)
        elif isinstance(v, list):
            for child in v:
                if isinstance(child, dict) and "id" in child:
                    visit(child, f"{path}.{child['id']}")

    visit(scene)
    edges = relationships(scene)
    return Evidence(
        image=scene["image"],
        recognition=diagnostics.get("recognition", {}),
        figure_regions=diagnostics.get("figure_regions", []),
        selected_region=scene["meta"].get("region"),
        detections=diagnostics.get("detections", []),
        objects=[
            ObjectEvidence(
                id=o["id"],
                type=o.get("type", "pulley"),
                detection_id=fits.get(o["id"], {}).get("detection_id"),
                measurement=fits.get(o["id"], {}),
            )
            for group in (scene["bodies"], scene["surfaces"], scene["links"], scene["pulleys"])
            for o in group
        ],
        ocr=diagnostics.get("texts", []),
        relationships=edges,
        hypotheses=diagnostics.get("hypotheses", []),
        assignments=diagnostics.get("assignments", []),
        unassigned_labels=[r for r in diagnostics.get("assignments", []) if not r["accepted"]],
        unresolved_attachments=[
            r.source
            for r in edges
            if r.state in {"assumed", "unresolved"}
            and r.type not in {"LABEL_OF", "ALTERNATE_STATE_OF"}
        ],
        assumptions=assumptions,
        warnings=scene["warnings"],
    )
