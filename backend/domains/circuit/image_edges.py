"""Conservative notice for ink cut by the original uploaded image boundary."""

import cv2
import numpy as np


def image_edge_cut(image: np.ndarray) -> bool:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
    # A continuous run avoids flagging isolated scan noise. This is evidence of
    # possible cropping, not proof that the missing content can be recovered.
    run = max(6, round(min(gray.shape) * 0.015))
    return any(
        np.convolve((edge < 100).astype(int), np.ones(run, dtype=int), "valid").max(initial=0)
        >= run
        for edge in [gray[0], gray[-1], gray[:, 0], gray[:, -1]]
        if len(edge) >= run
    )
