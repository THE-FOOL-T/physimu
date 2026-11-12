import cv2
import numpy as np
from circuit_sim.backend.pipeline.netlist import Component, Terminal
from circuit_sim.backend.pipeline.wires import trace


def symbol(id_, a, b):
    return Component(
        id=id_,
        type="resistor",
        bbox=(
            min(a[0], b[0]) - 1,
            min(a[1], b[1]) - 1,
            max(a[0], b[0]) + 1,
            max(a[1], b[1]) + 1,
        ),
        terminals=[
            Terminal(id=id_ + ".a", xy=a, node="x"),
            Terminal(id=id_ + ".b", xy=b, node="x"),
        ],
    )


def cross(dot=False):
    image = np.full((200, 200, 3), 255, np.uint8)
    cv2.line(image, (30, 100), (170, 100), (0, 0, 0), 2)
    cv2.line(image, (100, 30), (100, 170), (0, 0, 0), 2)
    if dot:
        cv2.circle(image, (100, 100), 6, (0, 0, 0), -1)
    cs = [
        symbol("L", (10, 100), (30, 100)),
        symbol("R", (170, 100), (190, 100)),
        symbol("T", (100, 10), (100, 30)),
        symbol("B", (100, 170), (100, 190)),
    ]
    return image, cs


def test_undotted_x_separates_channels():
    image, cs = cross()
    nodes, graph, warnings = trace(image, cs)
    assert cs[0].terminals[1].node == cs[1].terminals[0].node
    assert cs[2].terminals[1].node == cs[3].terminals[0].node
    assert cs[0].terminals[1].node != cs[2].terminals[1].node
    assert all(s.polyline for s in graph.segments)


def test_dotted_crossing_connects():
    image, cs = cross(True)
    trace(image, cs)
    assert (
        len(
            {
                cs[0].terminals[1].node,
                cs[1].terminals[0].node,
                cs[2].terminals[1].node,
                cs[3].terminals[0].node,
            }
        )
        == 1
    )


def test_t_junction_connects():
    image, cs = cross()
    image[102:, :, :] = 255
    cs = cs[:3]
    trace(image, cs)
    assert len({cs[0].terminals[1].node, cs[1].terminals[0].node, cs[2].terminals[1].node}) == 1
