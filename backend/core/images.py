"""Unchanged shared helpers extracted during M7."""

import base64
import cv2


def image_url(image):
    ok, data = cv2.imencode(".png", image)
    if not ok:
        return ""
    return "data:image/png;base64," + base64.b64encode(data).decode()
