"""Limit expensive detector retries to a few uncertain component neighborhoods."""

import copy


def recover(image, components, annotations, detector, check=lambda: None):
    h, w = image.shape[:2]
    uncertain = [c for c in components if c.confidence < 0.65]
    chosen = (
        uncertain
        or sorted(components, key=lambda c: (c.bbox[2] - c.bbox[0]) * (c.bbox[3] - c.bbox[1]))
    )[:4]
    result = copy.deepcopy(components)
    extra = list(annotations)
    windows = []

    def iou(a, b):
        overlap = max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(
            0, min(a[3], b[3]) - max(a[1], b[1])
        )
        return overlap / max(
            1, (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - overlap
        )

    for c in chosen:
        check()
        cx = (c.bbox[0] + c.bbox[2]) / 2
        cy = (c.bbox[1] + c.bbox[3]) / 2
        box = (
            max(0, int(cx - 256)),
            max(0, int(cy - 256)),
            min(w, int(cx + 256)),
            min(h, int(cy + 256)),
        )
        if any(iou(box, other) > 0.7 for other in windows):
            continue
        windows.append(box)
        x, y, x2, y2 = box
        found, marks = detector(image[y:y2, x:x2], threshold=0.12, tiled=False)
        for new in found:
            new.bbox = tuple(v + (x if k % 2 == 0 else y) for k, v in enumerate(new.bbox))
            if any(new.type == old.type and iou(new.bbox, old.bbox) > 0.4 for old in result):
                continue
            new.id = "retry." + str(len(result)) + "." + new.id
            positive = next(
                (
                    index
                    for index, t in enumerate(new.terminals)
                    if new.polarity and t.id == new.polarity.positive_terminal
                ),
                0,
            )
            for index, terminal in enumerate(new.terminals):
                terminal.xy = (terminal.xy[0] + x, terminal.xy[1] + y)
                terminal.id = new.id + (".a" if index == 0 else ".b")
            if new.polarity:
                new.polarity.positive_terminal = new.terminals[positive].id
            result.append(new)
        for mark in marks:
            mark = copy.deepcopy(mark)
            mark["bbox"] = [v + (x if k % 2 == 0 else y) for k, v in enumerate(mark["bbox"])]
            extra.append(mark)
    return result, extra
