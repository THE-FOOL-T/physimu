"""Diagram symbols and geometry-preserving scan/pen augmentation."""

import io
import math
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def font(size=18):
    import matplotlib

    return ImageFont.truetype(
        str(Path(matplotlib.get_data_path()) / "fonts/ttf/DejaVuSans.ttf"), size
    )


def symbol(draw, kind, a, b, rng, hand=False, iec=False, closed=True, positive_first=True):
    cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    angle = math.atan2(b[1] - a[1], b[0] - a[0])
    length = math.dist(a, b)

    def xy(p):
        return (
            cx + p[0] * math.cos(angle) - p[1] * math.sin(angle),
            cy + p[0] * math.sin(angle) + p[1] * math.cos(angle),
        )

    def line(points, width=3):
        points = [xy(p) for p in points]
        for start, end in zip(points, points[1:]):
            count = max(2, int(math.dist(start, end) / 5))
            dense = [
                (
                    start[0]
                    + (end[0] - start[0]) * i / count
                    + (rng.uniform(-1, 1) if hand else 0),
                    start[1]
                    + (end[1] - start[1]) * i / count
                    + (rng.uniform(-1, 1) if hand else 0),
                )
                for i in range(count + 1)
            ]
            for i in range(len(dense) - 1):
                if hand and rng.random() < 0.025:
                    continue
                draw.line(
                    dense[i : i + 2],
                    fill=(40, 42, 45) if hand else "black",
                    width=max(1, width + (rng.choice([-1, 0, 1]) if hand else 0)),
                )

    def circle(radius=18):
        line(
            [(radius * math.cos(t), radius * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 33)]
        )

    line([(-length / 2, 0), (-22, 0)])
    line([(22, 0), (length / 2, 0)])
    if kind in {
        "dc_source",
        "voltage_source",
        "ac_source",
        "current_source",
        "ammeter",
        "voltmeter",
        "galvanometer",
        "lamp",
    }:
        circle()
        if kind in {"ammeter", "voltmeter", "galvanometer"}:
            draw.text(
                (cx - 6, cy - 10),
                {"ammeter": "A", "voltmeter": "V", "galvanometer": "G"}[kind],
                font=font(16),
                fill="black",
            )
        elif kind == "lamp":
            line([(-12, -12), (12, 12)])
            line([(-12, 12), (12, -12)])
        elif kind == "ac_source":
            line([(x, 7 * math.sin(x / 5)) for x in np.linspace(-13, 13, 20)])
        elif kind == "current_source":
            line([(-12, 0), (12, 0), (5, -5)])
            line([(12, 0), (5, 5)])
        else:
            sign = 1 if positive_first else -1
            line([(-9 * sign, -5), (-9 * sign, 5)])
            line([(-14 * sign, 0), (-4 * sign, 0)])
            line([(6 * sign, 0), (14 * sign, 0)])
    elif kind == "battery":
        for x, size in [(-12, 17), (-5, 9), (5, 17), (12, 9)]:
            x = x if positive_first else -x
            line([(x, -size), (x, size)])
        line([(-22, 0), (-12, 0)])
        line([(12, 0), (22, 0)])
    elif kind == "capacitor":
        line([(-22, 0), (-5, 0)])
        line([(-5, -17), (-5, 17)])
        line([(5, -17), (5, 17)])
        line([(5, 0), (22, 0)])
    elif kind == "inductor":
        line(
            [
                (-22, 0),
                *[
                    (x, -10 * abs(math.sin((x + 20) * math.pi / 10)))
                    for x in np.linspace(-20, 20, 80)
                ],
                (22, 0),
            ]
        )
    elif kind == "switch":
        line([(-22, 0), (-12, 0), (15, 0 if closed else -14)])
        line([(15, 0), (22, 0)])
        for x in [-12, 15]:
            draw.ellipse([cx + x - 2, cy - 2, cx + x + 2, cy + 2], outline="black", width=2)
    elif kind == "diode":
        line([(-22, 0), (-12, 0), (-12, -13), (12, 0), (-12, 13), (-12, 0)])
        line([(12, -14), (12, 14)])
        line([(12, 0), (22, 0)])
    else:
        if iec or kind == "fuse":
            line([(-22, -9), (22, -9), (22, 9), (-22, 9), (-22, -9)])
        else:
            line(
                [
                    (-22, 0),
                    *[(x, 9 if i % 2 else -9) for i, x in enumerate(np.linspace(-20, 20, 9))],
                    (22, 0),
                ]
            )
        if kind == "fuse":
            line([(-22, 0), (22, 0)])
        if kind in {"rheostat", "potentiometer"}:
            line([(-20, 18), (20, -18), (9, -15)])
            line([(20, -18), (17, -7)])


def augment(image, net, boxes, seed, hand=False):
    rng = np.random.default_rng(seed)
    # Rotate the complete scene and every coordinate with the identical transform.
    angle = (seed % 4) * 90 + float(rng.uniform(-5, 5))
    w, h = image.size
    matrix = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1)
    neww = math.ceil(abs(matrix[0, 0]) * w + abs(matrix[0, 1]) * h)
    newh = math.ceil(abs(matrix[0, 1]) * w + abs(matrix[0, 0]) * h)
    matrix[:, 2] += [(neww - w) / 2, (newh - h) / 2]
    raster = cv2.warpAffine(np.asarray(image), matrix, (neww, newh), borderValue=(255, 255, 255))

    def xy(point):
        p = matrix @ np.array([*point, 1.0])
        if hand:
            p += np.array([1.5 * math.sin(p[1] / 60), 1.5 * math.sin(p[0] / 70)])
        return tuple(map(float, p))

    def bbox(box):
        x, y, x2, y2 = box
        corners = [xy(p) for p in [(x, y), (x2, y), (x, y2), (x2, y2)]]
        return (
            max(0, min(p[0] for p in corners) - 2),
            max(0, min(p[1] for p in corners) - 2),
            min(neww, max(p[0] for p in corners) + 2),
            min(newh, max(p[1] for p in corners) + 2),
        )

    if hand:
        yy, xx = np.mgrid[:newh, :neww].astype(np.float32)
        # Invert the smooth forward displacement by fixed-point iteration.
        sx, sy = xx.copy(), yy.copy()
        for _ in range(4):
            sx = xx - 1.5 * np.sin(sy / 60)
            sy = yy - 1.5 * np.sin(sx / 70)
        raster = cv2.remap(
            raster,
            sx,
            sy,
            cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255),
        )
    for c in net.components:
        c.bbox = bbox(c.bbox)
        c.orientation_deg = (c.orientation_deg - angle) % 360
        for terminal in c.terminals:
            terminal.xy = xy(terminal.xy)
    for p in net.wire_graph.points:
        p.xy = xy(p.xy)
    for s in net.wire_graph.segments:
        s.polyline = [xy(p) for p in s.polyline]
    boxes = [(cls, bbox(box)) for cls, box in boxes]
    # Monochrome paper texture, variable stroke intensity, blur and JPEG artifacts.
    texture = rng.normal(-4, 2, (newh, neww, 1)) + 3 * np.sin(np.arange(newh)[:, None, None] / 100)
    raster = np.clip(raster.astype(float) + texture, 0, 255).astype(np.uint8)
    image = Image.fromarray(raster).filter(ImageFilter.GaussianBlur(float(rng.uniform(0.1, 0.6))))
    if hand:
        draw = ImageDraw.Draw(image)
        for _ in range(8):
            x = int(rng.integers(0, neww))
            y = int(rng.integers(0, newh))
            draw.line(
                [(x, y), (x + int(rng.integers(2, 8)), y + 2)],
                fill=(242, 240, 234),
                width=2,
            )
    out = io.BytesIO()
    image.save(out, format="JPEG", quality=int(rng.integers(65, 95)))
    out.seek(0)
    image = Image.open(out).convert("RGB")
    net.image.width, net.image.height = image.size
    net.meta.provenance = (
        "synthetic intended graph; transformed coordinates; stroke perturbations bounded by 2 px"
    )
    return image, net, boxes
