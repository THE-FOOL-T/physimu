"""Tesseract consumes the same cleaned native, enlarged regions as EasyOCR."""

from functools import lru_cache
import time
import cv2
import numpy as np

from .ocr_tiles import candidate_regions, merge, windows
from .ocr_regions import anchored_regions


@lru_cache(maxsize=4)
def languages(binary):
    import pytesseract

    pytesseract.pytesseract.tesseract_cmd = binary
    available = pytesseract.get_languages(config="")
    return "+".join(language for language in ["eng", "ben"] if language in available) or "eng"


def recognize(image, binary, components, deadline, check=lambda: None):
    import pytesseract

    pytesseract.pytesseract.tesseract_cmd = binary
    image, proposals = anchored_regions(image, components, candidate_regions)
    for x, y, x2, y2 in windows(image):
        check()
        proposals.extend(
            {"text": "", "bbox": [a + x, b + y, c + x, d + y], "confidence": 0.5}
            for a, b, c, d in candidate_regions(image[y:y2, x:x2])
        )
    proposals = merge(proposals)[:64]
    crops = []
    height = 8
    width = 1
    for proposal in proposals:
        check()
        x, y, x2, y2 = map(int, proposal["bbox"])
        gray = cv2.cvtColor(image[y:y2, x:x2], cv2.COLOR_BGR2GRAY)
        rotations = [0] if gray.shape[0] <= gray.shape[1] * 1.35 else [90, -90]
        for angle in rotations:
            raw = (
                gray
                if not angle
                else cv2.rotate(
                    gray,
                    cv2.ROTATE_90_CLOCKWISE if angle == 90 else cv2.ROTATE_90_COUNTERCLOCKWISE,
                )
            )
            factor = max(1, 44 / max(1, raw.shape[0] - 10))
            enlarged = cv2.resize(raw, None, fx=factor, fy=factor, interpolation=cv2.INTER_CUBIC)
            crops.append((proposal, enlarged, height, angle))
            height += enlarged.shape[0] + 16
            width = max(width, enlarged.shape[1] + 16)
    if not crops or time.monotonic() >= deadline:
        return []
    atlas = np.full((height, width), 255, np.uint8)
    for _, gray, top, _ in crops:
        atlas[top : top + gray.shape[0], 8 : 8 + gray.shape[1]] = gray
    check()
    data = pytesseract.image_to_data(
        atlas,
        lang=languages(binary),
        config="--psm 11",
        output_type=pytesseract.Output.DICT,
        timeout=max(0.1, min(5, deadline - time.monotonic())),
    )
    groups = {}
    for i, text in enumerate(data["text"]):
        if not text.strip() or float(data["conf"][i]) < 0:
            continue
        cy = data["top"][i] + data["height"][i] / 2
        index = next(
            (j for j, (_, gray, top, _) in enumerate(crops) if top <= cy < top + gray.shape[0]),
            None,
        )
        if index is not None:
            groups.setdefault(index, []).append(
                (data["left"][i], text.strip(), float(data["conf"][i]) / 100)
            )
    items = []
    for index, words in groups.items():
        proposal, _, _, angle = crops[index]
        words.sort()
        items.append(
            {
                **proposal,
                "text": " ".join(word[1] for word in words),
                "confidence": sum(word[2] for word in words) / len(words),
                "engine": "tesseract",
                "rotation": angle,
            }
        )
    return items
