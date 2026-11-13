"""Manually inspected geometry on five real textbook images; never training labels."""

import json
from pathlib import Path
import shutil
from ..domains.circuit.netlist import *

from ..core.config import load_config

ROOT = Path(__file__).resolve().parents[2]

SOURCE = Path(load_config()["images"])


def make(name, file, component_specs, wire_specs):
    from PIL import Image as PILImage

    public = ROOT / "frontend/public/demos"
    public.mkdir(parents=True, exist_ok=True)
    image_name = name + ".png"
    shutil.copy2(SOURCE / file, public / image_name)
    with PILImage.open(SOURCE / file) as im:
        w, h = im.size
    cs = []
    points = {}
    segments = []
    for id_, kind, value, a, b, axy, bxy in component_specs:
        ts = [
            Terminal(id=id_ + ".a", node=a, xy=axy),
            Terminal(id=id_ + ".b", node=b, xy=bxy),
        ]
        unit = "V" if kind == "dc_source" else "ohm"
        cs.append(
            Component(
                id=id_,
                label=id_,
                type=kind,
                terminals=ts,
                bbox=(
                    min(axy[0], bxy[0]) - 8,
                    min(axy[1], bxy[1]) - 8,
                    max(axy[0], bxy[0]) + 8,
                    max(axy[1], bxy[1]) + 8,
                ),
                orientation_deg=90 if abs(axy[1] - bxy[1]) > abs(axy[0] - bxy[0]) else 0,
                value=Value(
                    number=value,
                    unit=unit,
                    status="given" if value is not None else "assumed",
                    source="user" if value is not None else "prior",
                    confidence=1 if value is not None else 0,
                ),
                polarity=Polarity(positive_terminal=id_ + ".a") if kind == "dc_source" else None,
                confidence=1,
            )
        )
        for t in ts:
            points[t.id] = Point(id=t.id, xy=t.xy, node=t.node, kind="terminal")
    for node, start, end, polyline in wire_specs:
        for id_, xy in [(start, polyline[0]), (end, polyline[-1])]:
            if id_ not in points:
                points[id_] = Point(id=id_, xy=xy, node=node, kind="junction")
        segments.append(
            Segment(
                id=f"w{len(segments) + 1}",
                from_=start,
                to=end,
                node=node,
                polyline=polyline,
                confidence=1,
            )
        )
    nodes = list(dict.fromkeys(t.node for c in cs for t in c.terminals))
    net = Netlist(
        image=Image(path="/demos/" + image_name, width=w, height=h),
        components=cs,
        nodes=[Node(id=n, is_ground=n == "g") for n in nodes],
        wire_graph=WireGraph(points=list(points.values()), segments=segments),
        meta=Meta(
            provenance="manually authored from source image; values absent from image are assumed"
        ),
    )
    for c in cs:
        if c.type == "switch":
            c.switch_closed = False
        if c.value.number is None:
            c.value.number = (
                12 if c.type == "dc_source" else 10 * (int(c.id[-1]) if c.id[-1].isdigit() else 1)
            )
            net.warn("assumed_value", c.id)
    (public / (name + ".json")).write_text(json.dumps(net.as_dict(), indent=2), encoding="utf-8")
    return {
        "id": name,
        "title": name.replace("-", " ").title(),
        "netlist": "/demos/" + name + ".json",
    }


def main():
    records = []
    records.append(
        make(
            "parallel-three",
            "Screenshot 2026-10-30 232522.png",
            [
                ("R1", "resistor", None, "p", "g", (222, 69), (348, 69)),
                ("R2", "resistor", None, "p", "g", (222, 140), (357, 140)),
                ("R3", "resistor", None, "p", "g", (222, 211), (348, 211)),
                ("V1", "dc_source", None, "p", "return", (278, 322), (303, 322)),
                ("S1", "switch", 0.001, "return", "g", (389, 322), (425, 322)),
            ],
            [
                ("p", "A", "R1.a", [(42, 142), (222, 69)]),
                ("p", "A", "R2.a", [(42, 142), (222, 140)]),
                ("p", "A", "R3.a", [(42, 142), (222, 211)]),
                ("p", "V1.a", "A", [(278, 322), (42, 325), (42, 142)]),
                ("g", "R1.b", "B", [(348, 69), (537, 137)]),
                ("g", "R2.b", "B", [(357, 140), (537, 137)]),
                ("g", "R3.b", "B", [(348, 211), (537, 137)]),
                ("g", "B", "S1.b", [(537, 137), (537, 321), (425, 322)]),
                ("return", "S1.a", "V1.b", [(389, 322), (303, 322)]),
            ],
        )
    )
    records.append(
        make(
            "parallel-two",
            "Screenshot 2026-10-30 232632.png",
            [
                ("R1", "resistor", None, "p", "g", (219, 46), (363, 46)),
                ("R2", "resistor", None, "p", "g", (219, 184), (363, 184)),
                ("V1", "dc_source", None, "p", "g", (273, 269), (294, 269)),
            ],
            [
                ("p", "A", "R1.a", [(117, 108), (117, 46), (219, 46)]),
                ("p", "A", "R2.a", [(117, 108), (117, 184), (219, 184)]),
                ("p", "V1.a", "A", [(273, 269), (31, 269), (31, 109), (117, 108)]),
                ("g", "R1.b", "B", [(363, 46), (465, 46), (465, 108)]),
                ("g", "R2.b", "B", [(363, 184), (465, 184), (465, 108)]),
                ("g", "B", "V1.b", [(465, 108), (548, 110), (548, 269), (294, 269)]),
            ],
        )
    )
    records.append(
        make(
            "mixed-network",
            "Screenshot 2026-10-30 232905.png",
            [
                ("R1", "resistor", 5000, "p", "a", (153, 47), (201, 47)),
                ("R2", "resistor", 10000, "a", "b", (267, 179), (267, 229)),
                ("R3", "resistor", 6000, "a", "c", (422, 111), (422, 163)),
                ("R4", "resistor", 3000, "a", "c", (532, 111), (532, 162)),
                ("R5", "resistor", 8000, "c", "b", (422, 262), (422, 315)),
                ("R6", "resistor", 2000, "b", "g", (202, 357), (153, 357)),
                ("V1", "dc_source", 24, "p", "g", (45, 187), (45, 218)),
            ],
            [
                ("p", "V1.a", "R1.a", [(45, 187), (45, 47), (153, 47)]),
                ("a", "R1.b", "J1", [(201, 47), (267, 47)]),
                ("a", "J1", "R2.a", [(267, 47), (267, 179)]),
                ("a", "J1", "J2", [(267, 47), (422, 47)]),
                ("a", "J2", "R3.a", [(422, 47), (422, 111)]),
                ("a", "J2", "R4.a", [(422, 47), (532, 47), (532, 111)]),
                ("c", "R3.b", "J3", [(422, 163), (422, 224)]),
                ("c", "R4.b", "J3", [(532, 162), (532, 224), (422, 224)]),
                ("c", "J3", "R5.a", [(422, 224), (422, 262)]),
                ("b", "R5.b", "J4", [(422, 315), (422, 357), (267, 357)]),
                ("b", "R2.b", "J4", [(267, 229), (267, 357)]),
                ("b", "J4", "R6.a", [(267, 357), (202, 357)]),
                ("g", "R6.b", "V1.b", [(153, 357), (45, 357), (45, 218)]),
            ],
        )
    )
    records.append(
        make(
            "loaded-bridge",
            "Screenshot 2026-10-30 232921.png",
            [
                ("V1", "dc_source", 10, "p", "g", (78, 150), (78, 198)),
                ("R1", "resistor", 1000, "p", "a", (146, 102), (200, 102)),
                ("R2", "resistor", 3000, "a", "b", (337, 102), (390, 102)),
                ("R3", "resistor", 2200, "a", "d", (267, 148), (267, 201)),
                ("R4", "resistor", 3000, "d", "g", (200, 245), (146, 245)),
                ("R5", "resistor", 10000, "c", "d", (390, 245), (337, 245)),
                ("R6", "resistor", 3000, "b", "c", (457, 148), (457, 201)),
            ],
            [
                ("p", "V1.a", "R1.a", [(78, 150), (78, 102), (146, 102)]),
                ("a", "R1.b", "A", [(200, 102), (267, 102)]),
                ("a", "A", "R2.a", [(267, 102), (337, 102)]),
                ("a", "A", "R3.a", [(267, 102), (267, 148)]),
                ("b", "R2.b", "R6.a", [(390, 102), (457, 102), (457, 148)]),
                ("c", "R6.b", "R5.a", [(457, 201), (457, 245), (390, 245)]),
                ("d", "R5.b", "D", [(337, 245), (267, 245)]),
                ("d", "R3.b", "D", [(267, 201), (267, 245)]),
                ("d", "D", "R4.a", [(267, 245), (200, 245)]),
                ("g", "R4.b", "V1.b", [(146, 245), (78, 245), (78, 198)]),
            ],
        )
    )
    records.append(
        make(
            "series-parallel",
            "Screenshot 2026-10-30 234104.png",
            [
                ("V1", "dc_source", 230, "p", "g", (63, 89), (63, 105)),
                ("R1", "resistor", 10, "p", "g", (117, 86), (117, 123)),
                ("R2", "resistor", 5, "p", "a", (142, 38), (188, 38)),
                ("R3", "resistor", 10, "a", "g", (197, 74), (197, 119)),
                ("R4", "resistor", 10, "a", "g", (257, 82), (257, 122)),
            ],
            [
                ("p", "V1.a", "P", [(63, 89), (63, 38), (117, 38)]),
                ("p", "P", "R1.a", [(117, 38), (117, 86)]),
                ("p", "P", "R2.a", [(117, 38), (142, 38)]),
                ("a", "R2.b", "A", [(188, 38), (197, 38)]),
                ("a", "A", "R3.a", [(197, 38), (197, 74)]),
                ("a", "A", "R4.a", [(197, 38), (257, 38), (257, 82)]),
                ("g", "V1.b", "G", [(63, 105), (63, 148), (117, 148)]),
                ("g", "R1.b", "G", [(117, 123), (117, 148)]),
                ("g", "G", "H", [(117, 148), (197, 148)]),
                ("g", "R3.b", "H", [(197, 119), (197, 148)]),
                ("g", "H", "R4.b", [(197, 148), (257, 148), (257, 122)]),
            ],
        )
    )
    (ROOT / "frontend/public/demos/index.json").write_text(json.dumps(records, indent=2))
    print("Created five source-aligned manual demos")


if __name__ == "__main__":
    main()
