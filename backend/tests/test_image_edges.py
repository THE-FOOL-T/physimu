import numpy as np
from backend.pipeline.image_edges import image_edge_cut


def test_border_notice_for_each_edge_without_flagging_interior_or_noise():
    for edge in range(4):
        image = np.full((100, 200, 3), 255, np.uint8)
        if edge == 0:
            image[0, 30:50] = 0
        elif edge == 1:
            image[-1, 30:50] = 0
        elif edge == 2:
            image[30:50, 0] = 0
        else:
            image[30:50, -1] = 0
        assert image_edge_cut(image)
    image = np.full((100, 200, 3), 255, np.uint8)
    image[40:60, 70:90] = 0
    image[0, 2] = 0
    assert not image_edge_cut(image)
