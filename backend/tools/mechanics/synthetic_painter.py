"""Styled M2 primitives with explicit object masks; this is rendering, not perception."""

import math

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

from .common import ROOT
from .paint_scene import spring_points
from .handwriting import label_mask
from .textbook import FILLS, spring_path


def font_for(size, variant):
    if variant:
        return ImageFont.truetype(str(ROOT / "frontend/public/fonts/NotoSansBengali.ttf"), size)
    return ImageFont.load_default(size=size)


def render(
    scene,
    rng,
    *,
    style,
    font_size,
    font_variant,
    arrow_style,
    hatch_spacing,
    mirror_text=False,
    handwriting="baseline",
    appearance="baseline",
):
    """Return RGB, amodal native mask per object, and their explicit detector classes."""
    if appearance not in {"baseline", "textbook"}:
        raise ValueError("Unknown appearance profile")
    varied = appearance == "textbook"
    image = Image.new("RGB", (scene.image.width, scene.image.height), scene.frame.paper_color)
    objects = []
    ink, stroke = scene.frame.ink_color, scene.frame.stroke_px
    strong = style == "handwritten" and handwriting == "strong"
    jitter = 2.5 if strong else 1.5 if style == "handwritten" else 0
    font = font_for(font_size, font_variant)

    def object_mask(name, id, draw_fn, *, fill=False):
        mask = Image.new("L", image.size)
        draw_fn(ImageDraw.Draw(mask), 255)
        box = mask.getbbox()
        if not box:
            raise ValueError(f"Empty synthetic object {id}")
        if name == "text_label" and mirror_text:
            # The final scene reflection must not produce backwards training text.
            mask.paste(ImageOps.mirror(mask.crop(box)), box[:2])
        if fill:
            image.paste(scene.frame.paper_color, (0, 0), mask)
        colour = Image.new("RGB", image.size, ink)
        image.paste(colour, (0, 0), mask)
        objects.append({"id": id, "class": name, "mask": mask})

    def line(draw, points, colour, *, arrow=False, closed=False):
        sampled = []
        for a, b in zip(points, points[1:]):
            n = max(1, round(math.dist(a, b) / 8))
            sampled.extend(
                [
                    (
                        a[0] + (b[0] - a[0]) * i / n + rng.uniform(-jitter, jitter),
                        a[1]
                        + (b[1] - a[1]) * i / n
                        + rng.uniform(-jitter, jitter)
                        + (1.5 * math.sin(i * 0.7) if strong else 0),
                    )
                    for i in range(n)
                ]
            )
        sampled.append(points[-1])
        width = max(1, round(stroke))
        if jitter:
            for a, b in zip(sampled, sampled[1:]):
                draw.line([a, b], fill=colour, width=max(1, width + rng.choice([-1, 0, 0, 1])))
        else:
            draw.line(sampled, fill=colour, width=width, joint="curve")
        if closed:
            draw.line([sampled[-1], sampled[0]], fill=colour, width=width)
        if arrow:
            a, b = points[-2], points[-1]
            angle = math.atan2(b[1] - a[1], b[0] - a[0])
            head = [
                (b[0] - 12 * math.cos(angle + d), b[1] - 12 * math.sin(angle + d))
                for d in (-0.42, 0.42)
            ]
            if arrow_style == "filled":
                draw.polygon([b, *head], fill=colour)
            else:
                draw.line([head[0], b, head[1]], fill=colour, width=width)

    for sf in scene.surfaces:
        object_mask(sf.type, sf.id, lambda d, c, sf=sf: line(d, sf.polyline, c))
        a, b = sf.polyline[0], sf.polyline[-1]
        length = math.dist(a, b)
        if length > 0:
            ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            segments = [
                [
                    (a[0] + ux * v - uy * 3, a[1] + uy * v + ux * 3),
                    (a[0] + ux * v - uy * 12 - ux * 7, a[1] + uy * v + ux * 12 - uy * 7),
                ]
                for v in range(hatch_spacing, round(length) - 4, hatch_spacing)
            ]
            if segments:
                object_mask(
                    "ground_hatch", f"hatch_{sf.id}", lambda d, c: [line(d, p, c) for p in segments]
                )
    for link in scene.links:
        points = (
            spring_points(link.a.point, link.b.point, link.coils or 10, rng.uniform(6, 12))
            if link.type == "spring"
            else link.polyline
        )
        if varied and link.type == "spring":
            points = spring_path(
                link.a.point,
                link.b.point,
                link.coils or 10,
                rng.uniform(9, 20),
                rng.choice([False, True]),
            )
        object_mask(link.type, link.id, lambda d, c, p=points: line(d, p, c))
    for pulley in scene.pulleys:
        x, y = pulley.center
        r = pulley.radius_px

        # Separate white fill from the instance region so rope behind the pulley is occluded.
        fill = rng.choice([scene.frame.paper_color, *FILLS]) if varied else scene.frame.paper_color
        ImageDraw.Draw(image).ellipse((x - r, y - r, x + r, y + r), fill=fill)
        object_mask(
            "pulley",
            pulley.id,
            lambda d, c, x=x, y=y, r=r: d.ellipse(
                (x - r, y - r, x + r, y + r), outline=c, width=max(1, round(stroke))
            ),
        )
        if varied:
            rim = r * rng.uniform(0.65, 0.85)
            draw = ImageDraw.Draw(image)
            draw.ellipse(
                (x - rim, y - rim, x + rim, y + rim), outline=ink, width=max(1, round(stroke))
            )
            spokes = rng.choice([0, 3, 4, 6])
            for i in range(spokes):
                angle = 2 * math.pi * i / spokes
                draw.line(
                    [(x, y), (x + rim * math.cos(angle), y + rim * math.sin(angle))],
                    fill=ink,
                    width=max(1, round(stroke)),
                )
        # White pulley interiors occlude links too. Fill instance ownership after
        # drawing the outline, without turning the actual pulley into solid ink.
        ImageDraw.Draw(objects[-1]["mask"]).ellipse((x - r, y - r, x + r, y + r), fill=255)
        ImageDraw.Draw(image).ellipse((x - 2, y - 2, x + 2, y + 2), fill=ink)
    for body in scene.bodies:
        x0, y0, x1, y1 = body.bbox
        if body.type in {"ball", "bob"}:
            centre = body.anchor
            polygon = [
                (
                    centre[0]
                    + (x1 - x0) / 2 * math.cos(i * math.pi / 32)
                    + rng.uniform(-jitter, jitter),
                    centre[1]
                    + (y1 - y0) / 2 * math.sin(i * math.pi / 32)
                    + rng.uniform(-jitter, jitter),
                )
                for i in range(64)
            ]
        else:
            polygon = list(body.mask)
        if body.type == "cart":
            polygon = [(x0, y0), (x1, y0), (x1, y1 - 10), (x0, y1 - 10)]
        fill = rng.choice([scene.frame.paper_color, *FILLS]) if varied else scene.frame.paper_color
        ImageDraw.Draw(image).polygon(polygon, fill=fill)

        def outline(d, c, p=polygon, cart=body.type == "cart", box=body.bbox):
            line(d, p + [p[0]], c, closed=True)
            if cart:
                a, b, z, v = box
                for x in (a + 10, z - 10):
                    d.ellipse((x - 5, v - 10, x + 5, v), fill=c)

        object_mask(body.type, body.id, outline)
        # Body masks include the interior and its exact closed drawn outline.
        ImageDraw.Draw(objects[-1]["mask"]).polygon(polygon, fill=255)
    for a in scene.annotations:
        g = a.geometry
        if a.type == "label" and g.text and g.bbox:
            x, y = g.bbox[:2]
            if strong:
                glyphs = label_mask(g.text, font, rng)
                object_mask(
                    "text_label", a.id, lambda d, c, x=x, y=y, m=glyphs: d.bitmap((x, y), m, fill=c)
                )
                continue
            object_mask(
                "text_label",
                a.id,
                lambda d, c, x=x, y=y, text=g.text: d.text((x, y), text, font=font, fill=c),
            )
        elif a.type == "angle_arc" and g.bbox:
            box = g.bbox
            object_mask(
                "angle_mark",
                a.id,
                lambda d, c, box=box, g=g: d.arc(
                    box, g.start_deg or 0, g.end_deg or 0, fill=c, width=max(1, round(stroke))
                ),
            )
        elif a.type == "dimension" and len(g.points) >= 2:
            object_mask("dimension_line", a.id, lambda d, c, p=g.points: line(d, p, c, arrow=True))
        elif a.type == "axis" and g.points:
            if len(g.points) == 1 and a.id != "pivot":
                # A wall/spring attachment is not a pendulum pivot symbol.
                continue
            name = (
                "pivot"
                if len(g.points) == 1
                else "arrow_velocity"
                if a.id.startswith("velocity") or a.id == "launch"
                else "trajectory_arc"
                if a.id.startswith("trajectory")
                else "axis"
            )
            if len(g.points) == 1:
                x, y = g.points[0]
                radius = rng.randint(6, 11) if varied else 4
                object_mask(
                    name,
                    a.id,
                    lambda d, c, x=x, y=y, r=radius: d.ellipse(
                        (x - r, y - r, x + r, y + r), fill=c
                    ),
                )
            else:
                object_mask(
                    name,
                    a.id,
                    lambda d, c, p=g.points, name=name: line(
                        d, p, c, arrow=name != "trajectory_arc"
                    ),
                )
    for force in scene.forces:
        object_mask(
            "arrow_force", force.id, lambda d, c, f=force: line(d, [f.tail, f.head], c, arrow=True)
        )
    return image, objects


def texture(image, rng, style):
    array = np.array(image, dtype=np.float32)
    h, w = array.shape[:2]
    if style in {"scan", "photo"}:
        noise = np.random.default_rng(rng.getrandbits(32)).normal(0, rng.uniform(1, 3), array.shape)
        array += noise
    if style == "photo":
        x = np.linspace(0, 1, w)[None, :]
        y = np.linspace(0, 1, h)[:, None]
        light = 0.76 + 0.20 * x + 0.08 * y
        centre = rng.uniform(0.2, 0.8)
        shadow = 1 - rng.uniform(0.08, 0.2) * np.exp(-(((x - centre) / 0.16) ** 2))
        array *= (light * shadow)[..., None]
    return Image.fromarray(np.uint8(np.clip(array, 0, 255)))
