"""Explicit opt-in correction storage; these are unreviewed, never gold."""

import json
import time
import uuid

import cv2

from ...core import decode
from .scene import Scene


def save_correction(data, scene_json, root):
    if not scene_json or len(scene_json) > 4_000_000:
        raise ValueError("Missing/oversized mechanics scene")
    try:
        scene = Scene.model_validate_json(scene_json)
        image = decode(data)
    except Exception as error:
        raise ValueError("Invalid scene or image") from error
    if (image.shape[1], image.shape[0]) != (scene.image.width, scene.image.height):
        raise ValueError("Image dimensions must match native scene coordinates")
    id_ = uuid.uuid4().hex
    dest = root / "data/corrections/mechanics" / id_
    dest.mkdir(parents=True)
    scene.image.path = "image.png"
    (dest / "scene.json").write_text(
        json.dumps(scene.model_dump(mode="json", by_alias=True), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    cv2.imwrite(str(dest / "image.png"), image)
    (dest / "consent.json").write_text(
        json.dumps(
            dict(
                opt_in=True,
                created_unix=time.time(),
                domain="mechanics",
                human_reviewed=False,
                provenance="user_correction_not_gold",
            )
        )
    )
    return dict(id=id_, saved=True, domain="mechanics", human_reviewed=False)
