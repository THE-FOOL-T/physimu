"""Reproducible synthetic oracle/geometry report. No real accuracy or model recall."""

import json
import math

import cv2
import numpy as np

from circuit_sim.backend.domains.mechanics import geometry
from circuit_sim.backend.domains.mechanics.engine import analyze_mechanics_page
from circuit_sim.backend.tests.mechanics.perception_fixtures import case
from circuit_sim.backend.tools.mechanics.build_fixtures import fixtures
from circuit_sim.backend.tools.mechanics.eval_end_to_end import (
    compare_scenes,
    trajectories,
    aggregate,
    PROTOCOL,
)
from circuit_sim.backend.tools.mechanics.paint_scene import spring_points


def measurements():
    def blank():
        return np.full((400, 600, 3), 255, np.uint8)

    lines = []
    for angle in [0, 15, 30, 60, 90, -30]:
        image = blank()
        a = np.array([150.0, 250.0])
        b = a + [200 * math.cos(math.radians(angle)), -200 * math.sin(math.radians(angle))]
        cv2.line(image, tuple(a.astype(int)), tuple(np.rint(b).astype(int)), (30, 30, 30), 2)
        fit = geometry.fit_line(image, [0, 0, 600, 400])
        lines.append(
            dict(
                truth_deg=angle,
                angle_error_deg=abs((fit["angle_deg"] - angle + 90) % 180 - 90),
                length_error_px=abs(fit["length_px"] - 200),
                residual_px=fit["residual_px"],
            )
        )
    image = blank()
    cv2.circle(image, (350, 250), 24, (30, 30, 30), 2)
    fit = geometry.fit_circle(image, [325, 224, 377, 275])
    pendulum = geometry.pendulum([250, 50], fit["center"])
    circle = dict(
        center_error_px=math.dist(fit["center"], [350, 250]),
        radius_error_px=abs(fit["radius_px"] - 24),
        pendulum_length_error_px=abs(pendulum["length_px"] - math.hypot(100, 200)),
        pendulum_angle_error_deg=abs(pendulum["angle_deg"] - math.degrees(math.atan(0.5))),
    )
    image = blank()
    pts = spring_points([80, 180], [400, 180], 10)
    cv2.polylines(image, [np.rint(pts).astype(np.int32)], False, (30, 30, 30), 2)
    fit = geometry.spring(image, [70, 155, 405, 205])
    spring = dict(
        truth_coils=10,
        measured_coils=fit["coils"],
        endpoint_errors_px=[
            math.dist(p, q) for p, q in zip(fit["endpoints"], [[80, 180], [400, 180]])
        ],
    )
    image = blank()
    points = [[x, 0.002 * (x - 200) ** 2 + 70] for x in np.linspace(50, 450, 250)]
    cv2.polylines(image, [np.rint(points).astype(np.int32)], False, (30, 30, 30), 2)
    fit = geometry.trajectory_arc(image, [40, 60, 460, 210], [50, 115])
    return dict(
        lines=lines,
        circle_pendulum=circle,
        spring=spring,
        trajectory=dict(
            tangent_error_deg=abs(fit["angle_deg"] - math.degrees(math.atan(0.6))),
            coefficient_error=abs(fit["coefficients"][0] - 0.002),
            residual_px=fit["residual_px"],
        ),
    )


def report():
    rows = []
    pairs = []
    for name in fixtures():
        image, truth, detector, reader = case(name)
        result = analyze_mechanics_page(
            image, dict(style="printed"), detector=detector, text_reader=reader
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
            diagnostics=result["diagnostics"],
        )
        rows.append(row)
        pairs.append(dict(prediction=result["scene"], gold=expected, body_map=row["body_map"]))
    for row, trajectory in zip(rows, trajectories(pairs)):
        row.update(trajectory)
    return dict(
        label="synthetic, not real accuracy",
        scope="10 M2 painted fixtures, oracle detector boxes and raw printed OCR; no archetype, attachment or scene injected; these QA fixtures are not held out",
        protocol=PROTOCOL,
        metrics=aggregate(rows),
        geometry=measurements(),
        records=rows,
        real_printed=None,
        real_handwritten=None,
        detector_recall=None,
    )


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
