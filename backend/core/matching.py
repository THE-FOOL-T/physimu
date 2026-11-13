"""Unchanged shared helpers extracted during M7."""


def center(box):
    return ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2)


def search_windows(component, shape=None):
    x, y, x2, y2 = component.bbox
    width, height = max(16, x2 - x), max(16, y2 - y)
    margin = min(110, max(36, max(width, height) * 0.8))
    boxes = [
        (x - margin, y - margin, x2 + margin, y + 4),
        (x - margin, y2 - 4, x2 + margin, y2 + margin),
        (x - margin, y - margin / 2, x + 4, y2 + margin / 2),
        (x2 - 4, y - margin / 2, x2 + margin, y2 + margin / 2),
        (x, y, x2, y2),
    ]
    if shape:
        h, w = shape[:2]
        boxes = [(max(0, a), max(0, b), min(w, c), min(h, d)) for a, b, c, d in boxes]
    return [tuple(map(int, b)) for b in boxes if b[2] > b[0] and b[3] > b[1]]
