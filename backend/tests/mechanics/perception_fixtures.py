"""Synthetic TEST oracles expose boxes/raw printed text only, never a result scene."""

import copy
from pathlib import Path

import cv2

from circuit_sim.backend.domains.mechanics.detect import Detection
from circuit_sim.backend.tools.mechanics.build_fixtures import fixtures
from circuit_sim.backend.tools.mechanics.paint_scene import spring_points

ROOT = Path(__file__).resolve().parents[3]


def box(points, pad=3):
    return [
        float(min(p[0] for p in points) - pad),
        float(min(p[1] for p in points) - pad),
        float(max(p[0] for p in points) + pad),
        float(max(p[1] for p in points) + pad),
    ]


def case(name):
    scene = fixtures()[name]
    image = cv2.imread(str(ROOT / "fixtures/mechanics" / (name + ".png")))
    boxes = []
    texts = []

    def add(type, bbox):
        boxes.append(Detection("test_" + str(len(boxes)), type, list(bbox), 1.0))

    for b in scene.bodies:
        add(b.type, b.bbox)
    for sf in scene.surfaces:
        add(sf.type, box(sf.polyline))
    for p in scene.pulleys:
        add(
            "pulley",
            [
                p.center[0] - p.radius_px,
                p.center[1] - p.radius_px,
                p.center[0] + p.radius_px,
                p.center[1] + p.radius_px,
            ],
        )
    for link in scene.links:
        add(
            link.type,
            box(
                spring_points(link.a.point, link.b.point, link.coils or 10)
                if link.type == "spring"
                else link.polyline,
                4,
            ),
        )
    for a in scene.annotations:
        if a.type == "axis" and a.geometry.points:
            if len(a.geometry.points) == 1 and a.id != "pivot":
                continue
            add(
                "pivot" if a.id == "pivot" else "arrow_velocity" if a.id == "launch" else "axis",
                box(a.geometry.points, 5),
            )
        elif a.type == "angle_arc" and a.geometry.bbox:
            add("angle_mark", a.geometry.bbox)
        elif a.type == "dimension" and a.geometry.points:
            add("dimension_line", box(a.geometry.points, 5))
        if a.geometry.text and a.geometry.bbox:
            add("text_label", a.geometry.bbox)
            texts.append(dict(text=a.geometry.text, bbox=list(a.geometry.bbox), confidence=1.0))
    for f in scene.forces:
        add("arrow_force", box([f.tail, f.head], 6))

    def detector(raster, check=lambda: None):
        check()
        return copy.deepcopy(boxes)

    def reader(raster, **kwargs):
        kwargs["check"]()
        return copy.deepcopy(texts), []

    return image, scene, detector, reader
