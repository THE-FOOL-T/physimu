"""Known synthetic handwriting measurements and detector/OCR-stub evidence, never real accuracy."""

import copy
import json
import math
import random

import cv2
import numpy as np

from circuit_sim.backend.domains.mechanics import geometry
from circuit_sim.backend.domains.mechanics.detect import Detection
from circuit_sim.backend.domains.mechanics.engine import analyze_mechanics_page
from circuit_sim.backend.tools.mechanics.build_fixtures import fixtures
from circuit_sim.backend.tools.mechanics.eval_end_to_end import (
    compare_scenes,
    aggregate,
    trajectories,
    PROTOCOL,
)
from circuit_sim.backend.tools.mechanics.paint_scene import spring_points
from circuit_sim.backend.tools.mechanics.synthetic_painter import render


def paper():
    return np.full((400, 600, 3), 255, np.uint8)


def measurements():
    lines = []
    for angle in (0, 15, 30, 60, 90, -30):
        image = paper()
        u = np.array([math.cos(math.radians(angle)), -math.sin(math.radians(angle))])
        n = np.array([-u[1], u[0]])
        ts = np.linspace(0, 200, 200)
        points = np.array([150, 250]) + ts[:, None] * u + (2.7 * np.sin(ts / 13))[:, None] * n
        cv2.polylines(image, [np.rint(points).astype(np.int32)], False, (25, 25, 25), 2)
        fit = geometry.fit_line(image, [0, 0, 600, 400], style="handwritten")
        lines.append(
            dict(
                truth_deg=angle,
                angle_error_deg=abs((fit["angle_deg"] - angle + 90) % 180 - 90),
                length_error_px=abs(fit["length_px"] - 200),
                residual_px=fit["residual_px"],
            )
        )
    image = paper()
    t = np.linspace(0, 2 * math.pi, 240)
    radii = 32 + 2.5 * np.sin(5 * t)
    points = np.stack([350 + radii * np.cos(t), 220 + radii * np.sin(t)], axis=1)
    cv2.polylines(image, [np.rint(points).astype(np.int32)], True, (25, 25, 25), 2)
    fit = geometry.fit_circle(image, [314, 184, 386, 256], style="handwritten")
    circle = dict(
        center_error_px=math.dist(fit["center"], [350, 220]),
        radius_error_px=abs(fit["radius_px"] - 32),
        residual_px=fit["residual_px"],
    )
    image = paper()
    points = np.array(spring_points([80, 180], [400, 180], 10))
    points[:, 1] += 1.5 * np.sin(points[:, 0] / 12)
    cv2.polylines(image, [np.rint(points).astype(np.int32)], False, (25, 25, 25), 2)
    fit = geometry.spring(image, [70, 155, 405, 205], style="handwritten")
    return dict(
        lines=lines,
        circle=circle,
        spring=dict(
            truth_coils=10,
            measured_coils=fit["coils"],
            endpoint_errors_px=[
                math.dist(a, b) for a, b in zip(fit["endpoints"], [[80, 180], [400, 180]])
            ],
        ),
    )


def case(name):
    truth = fixtures()[name]
    raster, objects = render(
        truth,
        random.Random(42),
        style="handwritten",
        handwriting="strong",
        font_size=17,
        font_variant=1,
        arrow_style="open",
        hatch_spacing=17,
    )
    image = cv2.cvtColor(np.array(raster), cv2.COLOR_RGB2BGR)
    boxes = [
        Detection(f"TEST-{i}", o["class"], list(o["mask"].getbbox()), 1.0)
        for i, o in enumerate(objects)
    ]
    labels = []
    for obj in objects:
        if obj["class"] == "text_label":
            annotation = next(a for a in truth.annotations if a.id == obj["id"])
            labels.append(
                dict(
                    text=annotation.geometry.text, bbox=list(obj["mask"].getbbox()), confidence=1.0
                )
            )

    def detector(image, check=lambda: None):
        check()
        return copy.deepcopy(boxes)

    def reader(image, **kwargs):
        kwargs["check"]()
        return copy.deepcopy(labels), []

    return image, truth, detector, reader


def report():
    rows, pairs = [], []
    for name in fixtures():
        image, truth, detector, reader = case(name)
        result = analyze_mechanics_page(
            image, dict(style="handwritten"), detector=detector, text_reader=reader
        )
        expected = truth.model_dump(mode="json", by_alias=True)
        row = compare_scenes(result["scene"], expected)
        row.update(
            name=name,
            expected_archetype=truth.archetype,
            actual_archetype=result["scene"]["archetype"],
            provenance=result["provenance"],
            timings=result["timings"],
            warnings=result["warnings"],
        )
        rows.append(row)
        pairs.append(dict(prediction=result["scene"], gold=expected, body_map=row["body_map"]))
    for row, trajectory in zip(rows, trajectories(pairs)):
        row.update(trajectory)
    return dict(
        label="synthetic, not real accuracy",
        scope="10 authored fixtures redrawn with strong pen jitter/digits/width variation; oracle boxes and raw text only, no result scene/archetype/attachments injected; no real handwriting",
        protocol=PROTOCOL,
        geometry=measurements(),
        metrics=aggregate(rows),
        records=rows,
        real_printed=None,
        real_handwritten=None,
        detector_accuracy=None,
        ocr_accuracy=None,
    )


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
