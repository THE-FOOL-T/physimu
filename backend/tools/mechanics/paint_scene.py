"""Deterministic printed primitives for authored fixtures (not a recognition benchmark).

Run as a module with a scene JSON and output PNG. No random state, fonts downloaded,
model inference, or model weights are involved. M4 can extend these primitives.
"""

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from ...domains.mechanics.scene import Scene


def spring_points(a, b, coils=10, amplitude=9):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    if length <= 24:
        return [a, b]
    ux, uy = dx / length, dy / length
    points = [a, (a[0] + ux * 12, a[1] + uy * 12)]
    for i in range(coils * 2 + 1):
        distance = 12 + (length - 24) * i / (coils * 2)
        offset = 0 if i in (0, coils * 2) else amplitude * (1 if i % 2 else -1)
        points.append((a[0] + ux * distance - uy * offset, a[1] + uy * distance + ux * offset))
    points.extend([(b[0] - ux * 12, b[1] - uy * 12), b])
    return points


def arrow(draw, a, b, color, width=2):
    draw.line([a, b], fill=color, width=width)
    angle = math.atan2(b[1] - a[1], b[0] - a[0])
    points = [b] + [
        (b[0] - 10 * math.cos(angle + d), b[1] - 10 * math.sin(angle + d)) for d in (-0.45, 0.45)
    ]
    draw.polygon(points, fill=color)


def paint_scene(scene: Scene) -> Image.Image:
    image = Image.new("RGB", (scene.image.width, scene.image.height), scene.frame.paper_color)
    draw = ImageDraw.Draw(image)
    ink, stroke = scene.frame.ink_color, round(scene.frame.stroke_px)
    font = ImageFont.load_default(size=16)
    for surface in scene.surfaces:
        draw.line(surface.polyline, fill=ink, width=stroke)
        a, b = surface.polyline[0], surface.polyline[-1]
        length = math.dist(a, b)
        if length:
            ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            # Hatching is static and stays in the source pixels.
            for i in range(12, round(length), 15):
                x, y = a[0] + ux * i, a[1] + uy * i
                draw.line(
                    [(x - uy * 3, y + ux * 3), (x - uy * 11 - ux * 7, y + ux * 11 - uy * 7)],
                    fill=ink,
                    width=1,
                )
    for link in scene.links:
        points = (
            spring_points(link.a.point, link.b.point, link.coils or 10)
            if link.type == "spring"
            else link.polyline
        )
        draw.line(points, fill=ink, width=stroke, joint="curve")
    for pulley in scene.pulleys:
        x, y = pulley.center
        r = pulley.radius_px
        draw.ellipse(
            (x - r, y - r, x + r, y + r), fill=scene.frame.paper_color, outline=ink, width=stroke
        )
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=ink)
    for annotation in scene.annotations:
        if annotation.type == "axis" and len(annotation.geometry.points) >= 2:
            arrow(draw, annotation.geometry.points[0], annotation.geometry.points[-1], ink, stroke)
    for body in scene.bodies:
        if body.type in ("ball", "bob"):
            draw.ellipse(body.bbox, fill=scene.frame.paper_color, outline=ink, width=stroke)
        else:
            # Rotation is encoded by the authored mask; inset avoids cutting its ink.
            polygon = [(x, y) for x, y in body.mask]
            if body.type == "cart":
                draw.rectangle(body.bbox, fill=scene.frame.paper_color, outline=ink, width=stroke)
            else:
                draw.polygon(polygon, fill=scene.frame.paper_color)
                draw.line(polygon + polygon[:1], fill=ink, width=stroke, joint="curve")
    for annotation in scene.annotations:
        g = annotation.geometry
        if annotation.type == "dimension" and len(g.points) >= 2:
            arrow(draw, g.points[0], g.points[-1], ink, stroke)
        if annotation.type == "angle_arc" and g.bbox:
            draw.arc(g.bbox, g.start_deg or 0, g.end_deg or 0, fill=ink, width=stroke)
        if g.text and g.bbox:
            draw.text((g.bbox[0], g.bbox[1]), g.text, font=font, fill=ink)
    for force in scene.forces:
        arrow(draw, force.tail, force.head, ink, stroke)
    return image


def save_diagram(scene: Scene, output: Path):
    """Write the pixels and their exact authored masks/repairs in canonical JSON."""
    paint_scene(scene).save(output)
    document = scene.model_dump(mode="json", by_alias=True)
    document["image"]["path"] = output.name
    output.with_suffix(".json").write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scene", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    scene = Scene.model_validate_json(args.scene.read_text(encoding="utf-8"))
    save_diagram(scene, args.output)


if __name__ == "__main__":
    main()
