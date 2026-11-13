"""Generate labeled R/C/switch series-parallel circuits, including a jittered pen style."""

import argparse
import json
import math
from pathlib import Path
import random
import numpy as np
from PIL import Image as PILImage, ImageDraw, ImageFont, ImageFilter
import yaml
from ..domains.circuit.netlist import *

ROOT = Path(__file__).resolve().parents[2]


def generate(seed=0, hand_drawn=False, bangla=False, all_classes=False, augment_scene=False):
    names = yaml.safe_load((ROOT / "data/class_schema.yaml").read_text(encoding="utf-8"))["names"]
    rng = random.Random(seed)
    w, h = 1000, 660
    image = PILImage.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(str(ROOT / "frontend/public/fonts/NotoSansBengali.ttf"), 18)
    nodes = [Node(id="p"), Node(id="g", is_ground=True)]
    cs = []
    points = []
    segments = []
    boxes = []

    def line(poly, width=3):
        dense = []
        for a, b in zip(poly, poly[1:]):
            count = max(1, int(math.dist(a, b) / 12))
            dense.extend(
                [
                    (
                        a[0]
                        + (b[0] - a[0]) * i / count
                        + (rng.uniform(-1.3, 1.3) if hand_drawn else 0),
                        a[1]
                        + (b[1] - a[1]) * i / count
                        + (rng.uniform(-1.3, 1.3) if hand_drawn else 0),
                    )
                    for i in range(count)
                ]
            )
        draw.line(
            [*dense, poly[-1]],
            fill=(35, 38, 40) if hand_drawn else "black",
            width=width,
        )

    def comp(id_, kind, value, a, b, axy, bxy):
        x1, y1 = axy
        x2, y2 = bxy
        bbox = (min(x1, x2) - 7, min(y1, y2) - 21, max(x1, x2) + 7, max(y1, y2) + 21)
        c = Component(
            id=id_,
            type=kind,
            label=id_,
            bbox=bbox,
            terminals=[
                Terminal(id=id_ + ".a", xy=axy, node=a),
                Terminal(id=id_ + ".b", xy=bxy, node=b),
            ],
            value=Value(
                number=value,
                unit={
                    "dc_source": "V",
                    "battery": "V",
                    "ac_source": "V",
                    "current_source": "A",
                    "capacitor": "F",
                    "inductor": "H",
                }.get(kind, "ohm"),
                status="given",
                source="user",
                confidence=1,
            ),
            confidence=1,
            polarity=Polarity(positive_terminal=id_ + ".a")
            if kind in {"dc_source", "battery", "ac_source"}
            else None,
        )
        cs.append(c)
        for t in c.terminals:
            points.append(Point(id=t.id, xy=t.xy, node=t.node, kind="terminal"))
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2
        if all_classes:
            from .synthetic_symbols import symbol

            c.switch_closed = bool(seed % 2)
            positive_first = bool((seed // 4) % 2)
            if c.polarity:
                c.polarity.positive_terminal = c.terminals[0 if positive_first else 1].id
            symbol(
                draw,
                kind,
                axy,
                bxy,
                rng,
                hand_drawn,
                iec=bool(seed % 2),
                closed=c.switch_closed,
                positive_first=positive_first,
            )
        else:
            if kind == "dc_source":
                draw.ellipse([mx - 20, my - 20, mx + 20, my + 20], outline="black", width=3)
                line([(x1, y1), (mx - 20, my)])
                line([(mx + 20, my), (x2, y2)])
                draw.text((mx - 13, my - 13), "+ −", font=font, fill="black")
            elif kind == "capacitor":
                line([axy, (mx - 5, my)])
                line([(mx - 5, my - 15), (mx - 5, my + 15)])
                line([(mx + 5, my - 15), (mx + 5, my + 15)])
                line([(mx + 5, my), bxy])
            elif kind == "switch":
                line([axy, (mx - 12, my)])
                line([(mx - 12, my), (mx + 13, my - 12)])
                line([(mx + 13, my), bxy])
                c.switch_closed = False
            elif seed % 2:
                line([axy, (mx - 25, my)])
                draw.rectangle((mx - 25, my - 10, mx + 25, my + 10), outline="black", width=3)
                line([(mx + 25, my), bxy])
            else:
                line(
                    [
                        axy,
                        *[(mx - 28 + i * 7, my + (9 if i % 2 else -9)) for i in range(9)],
                        bxy,
                    ]
                )
        text = f"{id_} {value:g} " + (
            "V" if kind == "dc_source" else "F" if kind == "capacitor" else "Ω"
        )
        if all_classes:
            text = text.replace(chr(937), "ohm")
        if bangla:
            text = text.translate(str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯"))
        draw.text((mx - 35, my - 42), text, font=font, fill="black")
        boxes.append((names.index("voltage_source" if kind == "dc_source" else kind), bbox))
        if all_classes:
            boxes.append(
                (
                    names.index("text_label"),
                    draw.textbbox((mx - 35, my - 42), text, font=font),
                )
            )
        return c

    def wire(node, a, b, poly):
        for id_, xy in [(a, poly[0]), (b, poly[-1])]:
            if not any(p.id == id_ for p in points):
                points.append(Point(id=id_, xy=xy, node=node, kind="junction"))
        segments.append(
            Segment(
                id=f"w{len(segments) + 1}",
                from_=a,
                to=b,
                node=node,
                polyline=poly,
                confidence=1,
            )
        )
        line(poly)

    branches = rng.randint(2, 3)
    columns = rng.randint(2, 4)
    values = [10, 12, 15, 22, 33, 47, 68]
    for row in range(branches):
        y = 100 + row * 140
        for col in range(columns):
            x = 220 + col * 180
            id_ = f"R{row * columns + col + 1}"
            a = "p" if col == 0 else f"n{row}.{col}"
            b = "g" if col == columns - 1 else f"n{row}.{col + 1}"
            if col < columns - 1:
                nodes.append(Node(id=b))
            kind = (
                "capacitor"
                if seed % 5 == 0 and row == 0 and col == columns - 1
                else "switch"
                if seed % 7 == 0 and row == 1 and col == 0
                else "resistor"
            )
            if all_classes:
                kinds = [n for n in names[:17] if n != "ground"]
                kind = kinds[(seed + row * columns + col) % len(kinds)]
                kind = "dc_source" if kind == "voltage_source" else kind
            comp(
                id_,
                kind,
                1e-4 if kind == "capacitor" else 0.1 if kind == "inductor" else rng.choice(values),
                a,
                b,
                (x - 45, y),
                (x + 45, y),
            )
            if col == 0:
                wire("p", f"left{row}", id_ + ".a", [(90, y), (x - 45, y)])
            else:
                wire(
                    a,
                    f"R{row * columns + col}.b",
                    id_ + ".a",
                    [(x - 180 + 45, y), (x - 45, y)],
                )
            if col == columns - 1:
                wire("g", id_ + ".b", f"right{row}", [(x + 45, y), (920, y)])
        if row:
            wire("p", f"left{row - 1}", f"left{row}", [(90, y - 140), (90, y)])
            wire("g", f"right{row - 1}", f"right{row}", [(920, y - 140), (920, y)])
    source = comp("V1", "dc_source", rng.choice([6, 9, 12]), "p", "g", (470, 560), (530, 560))
    last_y = 100 + (branches - 1) * 140
    wire("p", "V1.a", f"left{branches - 1}", [(470, 560), (90, 560), (90, last_y)])
    wire("g", f"right{branches - 1}", "V1.b", [(920, last_y), (920, 560), (530, 560)])
    if hand_drawn:
        image = image.filter(ImageFilter.GaussianBlur(0.35))
    net = Netlist(
        image=Image(path=f"circuit_{seed:06}.png", width=w, height=h),
        components=cs,
        nodes=nodes,
        wire_graph=WireGraph(points=points, segments=segments),
        meta=Meta(
            provenance="extracted",
            style="handwritten" if hand_drawn else "printed",
        ),
    )
    if all_classes:

        def annotation(kind, box):
            boxes.append((names.index(kind), box))

        for row in range(branches):
            for x in [90, 920]:
                y = 100 + row * 140
                draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill="black")
                annotation("junction", (x - 5, y - 5, x + 5, y + 5))
        for marker, (x, y) in zip(
            "ABPQ", [(65, 80), (930, 80), (65, last_y - 20), (930, last_y - 20)]
        ):
            draw.text((x, y), marker, font=font, fill="black")
            annotation("terminal_marker", draw.textbbox((x, y), marker, font=font))
        draw.text((445, 580), "+ -", font=font, fill="black")
        annotation("plus_minus_mark", draw.textbbox((445, 580), "+ -", font=font))
        line([(340, 70), (390, 70), (380, 63)])
        line([(390, 70), (380, 77)])
        annotation("arrow", (338, 61, 392, 79))
        line([(920, last_y), (920, last_y + 30)])
        line([(905, last_y + 30), (935, last_y + 30)])
        line([(910, last_y + 36), (930, last_y + 36)])
        line([(915, last_y + 42), (925, last_y + 42)])
        annotation("ground", (903, last_y + 27, 937, last_y + 44))
        # The ground annotation attaches to the existing g node; it is not a two-port part.
        net.wire_graph.points.append(
            Point(id="ground-marker", xy=(920, last_y + 30), node="g", kind="terminal")
        )
        net.wire_graph.segments.append(
            Segment(
                id="ground-wire",
                from_=f"right{branches - 1}",
                to="ground-marker",
                node="g",
                polyline=[(920, last_y), (920, last_y + 30)],
                confidence=1,
            )
        )
    if augment_scene:
        from .synthetic_symbols import augment

        image, net, boxes = augment(image, net, boxes, seed, hand_drawn)
    return image, net, boxes


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--count", type=int, default=100)
    p.add_argument("--hand-drawn", action="store_true")
    p.add_argument("--bangla", action="store_true")
    p.add_argument("--legacy", action="store_true")
    args = p.parse_args()
    dest = Path(args.out)
    if dest.exists() and any(dest.iterdir()):
        p.error("Output must be new or empty")
    for sub in ["images", "labels", "netlists"]:
        (dest / sub).mkdir(parents=True, exist_ok=True)
    for seed in range(args.count):
        image, net, boxes = generate(
            seed,
            args.hand_drawn,
            args.bangla,
            all_classes=not args.legacy,
            augment_scene=not args.legacy,
        )
        name = f"circuit_{seed:06}"
        image.save(dest / "images" / (name + ".png"))
        (dest / "netlists" / (name + ".json")).write_text(
            json.dumps(net.as_dict(), indent=2), encoding="utf-8"
        )
        (dest / "labels" / (name + ".txt")).write_text(
            "\n".join(
                f"{cls} {(b[0] + b[2]) / (2 * image.width)} {(b[1] + b[3]) / (2 * image.height)} {(b[2] - b[0]) / image.width} {(b[3] - b[1]) / image.height}"
                for cls, b in boxes
            )
        )
    names = yaml.safe_load((ROOT / "data/class_schema.yaml").read_text(encoding="utf-8"))["names"]
    (dest / "data.yaml").write_text(
        yaml.safe_dump(
            {
                "path": str(dest.resolve()),
                "train": "images",
                "val": "images",
                "names": names,
            }
        )
    )
    (dest / "SOURCE.md").write_text(
        "Locally generated synthetic data. This is not a held-out real-world benchmark. Noto font uses OFL-1.1. Intended topology and transformed geometry are known; pen and elastic perturbations are bounded, with conservative boxes. Never use this as real-world accuracy.\n"
    )
    print(f"Generated {args.count} circuits; source images untouched")


if __name__ == "__main__":
    main()
