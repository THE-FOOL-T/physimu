"""Native-resolution OCR windows and geometry-preserving duplicate suppression."""

import math


def windows(image, components=None, side=1024, overlap=0.2):
    h, w = image.shape[:2]

    def starts(length):
        count = max(1, math.ceil(max(0, length - side) / (side * (1 - overlap))) + 1)
        return [round(i * max(0, length - side) / max(1, count - 1)) for i in range(count)]

    result = []
    for y in starts(h):
        for x in starts(w):
            box = (x, y, min(w, x + side), min(h, y + side))
            if components and not any(
                intersection(
                    box,
                    (
                        c.bbox[0] - 140,
                        c.bbox[1] - 140,
                        c.bbox[2] + 140,
                        c.bbox[3] + 140,
                    ),
                )
                > 0
                for c in components
            ):
                continue
            result.append(box)
    return result


def intersection(a, b):
    return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))


def candidate_regions(tile):
    """Cheap native text proposals; avoid applying CRAFT to large blank margins."""
    import cv2
    import numpy as np

    gray = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)
    ink = (gray < 180).astype(np.uint8) * 255
    # Long strokes are wires/ruling, rather than 10–14 pixel glyphs.
    for kernel in [(70, 1), (1, 70)]:
        ink = cv2.subtract(
            ink,
            cv2.morphologyEx(
                ink, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, kernel)
            ),
        )
    joined = cv2.dilate(ink, cv2.getStructuringElement(cv2.MORPH_RECT, (9, 3)))
    count, _, stats, _ = cv2.connectedComponentsWithStats(joined)
    regions = []
    for x, y, w, h, area in stats[1:count]:
        if 5 <= h <= 600 and 6 <= w <= 600 and min(h, w) <= 100 and area >= 12:
            regions.append(
                (
                    max(0, x - 5),
                    max(0, y - 5),
                    min(gray.shape[1], x + w + 5),
                    min(gray.shape[0], y + h + 5),
                )
            )
    return sorted(regions, key=lambda b: (b[1], b[0]))[:64]


def merge(items):
    kept = []
    for item in sorted(items, key=lambda i: -i["confidence"]):
        a = item["bbox"]
        area = max(1, (a[2] - a[0]) * (a[3] - a[1]))
        duplicate = False
        for other in kept:
            b = other["bbox"]
            barea = max(1, (b[2] - b[0]) * (b[3] - b[1]))
            shared = intersection(a, b)
            if shared / (area + barea - shared) > 0.35 or shared / min(area, barea) > 0.75:
                duplicate = True
                break
        if not duplicate:
            kept.append(item)
    return sorted(kept, key=lambda i: (i["bbox"][1], i["bbox"][0]))


def easy_tiles(
    image,
    reader,
    bn_reader_factory,
    components=None,
    handwritten=False,
    diagnostics=None,
    deadline=None,
    check=None,
):
    import cv2
    import numpy as np
    import time
    from .values import parse_value
    from .ocr_regions import (
        anchored_regions,
        crop_variants,
        failure,
        merge_readings,
        quality,
        unit_glyph_hint,
    )

    diagnostics = diagnostics if diagnostics is not None else {}
    deadline = deadline if deadline is not None else time.monotonic() + 16
    check = check or (lambda: None)
    original_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image, proposals = anchored_regions(image, components, candidate_regions)
    removed_strokes = (original_gray < 180) & (cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) >= 180)
    for x, y, x2, y2 in windows(image):
        check()
        for rx, ry, rx2, ry2 in candidate_regions(image[y:y2, x:x2]):
            box = (rx + x, ry + y, rx2 + x, ry2 + y)
            proposals.append({"text": "", "bbox": list(box), "confidence": 0.5})
    proposals = merge(proposals)[:64]
    if not proposals:
        return []
    # Pack native crops, enlarged for recognition, into an in-memory atlas. CRAFT
    # is not repeated for each word: CV detection already supplied their geometry.
    crops = []
    height = 8
    width = 1
    for proposal in proposals:
        x, y, x2, y2 = map(int, proposal["bbox"])
        crop = image[y:y2, x:x2]
        factor = max(1, 42 / max(crop.shape[0] * 0.6, crop.shape[0] - 12, 1))
        crop = cv2.resize(crop, None, fx=factor, fy=factor, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        crops.append((gray, x, y, x2, y2, height))
        height += gray.shape[0] + 8
        width = max(width, gray.shape[1] + 16)
    atlas = np.full((height, width), 255, np.uint8)
    boxes = []
    for gray, x, y, x2, y2, top in crops:
        atlas[top : top + gray.shape[0], 8 : 8 + gray.shape[1]] = gray
        boxes.append([8, 8 + gray.shape[1], top, top + gray.shape[0]])

    def recognized_batch(reader, indices):
        output = []
        check()
        for box, text, confidence in reader.recognize(
            atlas,
            horizontal_list=[boxes[i] for i in indices],
            free_list=[],
            detail=1,
            paragraph=False,
            batch_size=1,
            workers=0,
        ):
            cy = sum(p[1] for p in box) / len(box)
            index = next((i for i in indices if boxes[i][2] <= cy <= boxes[i][3]), None)
            if index is None:
                continue
            gray, x, y, x2, y2, top = crops[index]
            sx = gray.shape[1] / max(1, x2 - x)
            sy = gray.shape[0] / max(1, y2 - y)
            xs = [(p[0] - 8) / sx + x for p in box]
            ys = [(p[1] - top) / sy + y for p in box]
            output.append(
                (
                    index,
                    {
                        **proposals[index],
                        "text": text,
                        "bbox": [min(xs), min(ys), max(xs), max(ys)],
                        "confidence": float(confidence),
                        "engine": "easyocr",
                        "rotation": 0,
                    },
                )
            )
        return output

    from ..config import load_config

    component_seconds = load_config().get("analysis", {}).get("component_ocr_seconds", 1.5)
    spent = {}

    def recognized(reader, indices):
        output = []
        groups = {}
        for index in indices:
            groups.setdefault(proposals[index].get("component_id", "global"), []).append(index)
        for owner, group in groups.items():
            check()
            if time.monotonic() >= deadline:
                diagnostics["budget_exceeded"] = True
                break
            if spent.get(owner, 0) >= component_seconds:
                diagnostics.setdefault("component_budget_exceeded", []).append(owner)
                continue
            started = time.monotonic()
            output.extend(recognized_batch(reader, group))
            spent[owner] = spent.get(owner, 0) + time.monotonic() - started
        diagnostics["component_seconds"] = dict(spent)
        return output

    items = recognized(reader, list(range(len(crops))))
    ambiguous = []
    for index, item in items:
        parsed = parse_value(item["text"])
        if len(item["text"].strip()) > 1 and (
            item["confidence"] < 0.65
            or parsed is None
            or parsed["unit"] is None
            and not parsed["label"]
        ):
            ambiguous.append(index)
    ambiguous = ambiguous[: 8 if handwritten else 4]
    if ambiguous and time.monotonic() < deadline:
        try:
            replacements = dict(recognized(bn_reader_factory(), ambiguous))
            items = [
                (index, replacements[index])
                if index in replacements
                and parse_value(replacements[index]["text"])
                and replacements[index]["confidence"] > item["confidence"]
                else (index, item)
                for index, item in items
            ]
        except Exception as exc:
            failure(diagnostics, "easyocr-bn", exc)
    result = [item for _, item in items]
    retries = [
        item
        for item in result
        if (item["bbox"][3] - item["bbox"][1]) > 1.35 * (item["bbox"][2] - item["bbox"][0])
        or quality(item)[0] < 3
    ]
    if retries and (
        components
        or any(
            (item["bbox"][3] - item["bbox"][1]) > 1.35 * (item["bbox"][2] - item["bbox"][0])
            for item in retries
        )
    ):
        result.extend(crop_variants(image, retries, reader, deadline, diagnostics, check))
    if handwritten:
        for item in result:
            item["confidence"] *= 0.7
    for item in result:
        hint = unit_glyph_hint(image, item["bbox"])
        if hint:
            item.update(unit_hint=hint["unit"], glyph_count=hint["glyphs"])
        x, y, x2, y2 = map(int, item["bbox"])
        ink = original_gray[max(0, y) : max(0, y2), max(0, x) : max(0, x2)] < 180
        removed = removed_strokes[max(0, y) : max(0, y2), max(0, x) : max(0, x2)]
        item["wire_overlap"] = bool(np.count_nonzero(removed) / max(1, np.count_nonzero(ink)) > 0.2)
    return merge_readings(result)
