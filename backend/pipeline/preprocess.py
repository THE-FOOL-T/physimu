"""Image decoding, orientation, conservative photo cleanup and page segmentation."""

import io
import cv2
import numpy as np
from PIL import Image, ImageOps

MAX_BYTES = 20 * 1024 * 1024
MAX_PIXELS = 24_000_000


def decode(data, page=0):
    if len(data) > MAX_BYTES:
        raise ValueError("too_large")
    if data.startswith(b"%PDF-"):
        import pypdfium2

        document = pypdfium2.PdfDocument(data)
        try:
            if page < 0 or page >= len(document):
                raise ValueError("invalid_page")
            pdfpage = document[page]
            try:
                width, height = pdfpage.get_size()
                if width * height * (200 / 72) ** 2 > MAX_PIXELS:
                    raise ValueError("too_many_pixels")
                bitmap = pdfpage.render(scale=200 / 72)
                try:
                    im = bitmap.to_pil().convert("RGB").copy()
                finally:
                    bitmap.close()
            finally:
                pdfpage.close()
        finally:
            document.close()
    else:
        if data[4:8] == b"ftyp":
            import pillow_heif

            pillow_heif.register_heif_opener()
        im = Image.open(io.BytesIO(data))
        if im.width * im.height > MAX_PIXELS:
            raise ValueError("too_many_pixels")
        im = ImageOps.exif_transpose(im).convert("RGB")
    if im.width < 8 or im.height < 8:
        raise ValueError("too_small")
    image = cv2.cvtColor(np.asarray(im), cv2.COLOR_RGB2BGR)
    # Keep CV bounded on full camera frames. Returned image and geometry share this space.
    ratio = min(1, 1800 / max(image.shape[:2]))
    if ratio < 1:
        image = cv2.resize(image, None, fx=ratio, fy=ratio, interpolation=cv2.INTER_AREA)
    return image


def preprocess(image, style="auto", estimate=None):
    warnings = []
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    from .style import estimate_style, remove_ruling

    estimated = estimate if estimate is not None else estimate_style(image)
    image, removed = remove_ruling(image)
    if removed:
        warnings.append(("ruling_removed", None))
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    if min(gray.shape) < 160 or cv2.Laplacian(gray, cv2.CV_64F).var() < 35:
        warnings.append(("low_quality_image", None))
    # A photograph generally has broad illumination variation, unlike cropped scans.
    background = cv2.GaussianBlur(gray, (0, 0), 25)
    photo = (
        estimated["style"] == "photo"
        or float(np.std(background)) > 28
        and float(np.mean(gray < 220)) > 0.2
    )
    handwritten = style == "handwritten" or style == "auto" and estimated["style"] == "handwritten"
    if photo:
        edges = cv2.Canny(background, 40, 100)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        corrected = False
        for contour in sorted(contours, key=cv2.contourArea, reverse=True)[:5]:
            approx = cv2.approxPolyDP(contour, 0.025 * cv2.arcLength(contour, True), True)
            if len(approx) == 4 and cv2.contourArea(approx) > 0.5 * gray.size:
                ps = approx[:, 0, :].astype(np.float32)
                s = ps.sum(axis=1)
                d = np.diff(ps, axis=1)[:, 0]
                rect = np.array(
                    [ps[s.argmin()], ps[d.argmin()], ps[s.argmax()], ps[d.argmax()]],
                    np.float32,
                )
                w = int(
                    max(
                        np.linalg.norm(rect[0] - rect[1]),
                        np.linalg.norm(rect[2] - rect[3]),
                    )
                )
                h = int(
                    max(
                        np.linalg.norm(rect[0] - rect[3]),
                        np.linalg.norm(rect[1] - rect[2]),
                    )
                )
                if w > 100 and h > 100:
                    transform = cv2.getPerspectiveTransform(
                        rect,
                        np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], np.float32),
                    )
                    image = cv2.warpPerspective(image, transform, (w, h))
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    corrected = True
                break
        if not corrected:
            contour = max(contours, key=cv2.contourArea, default=None)
            if contour is not None and cv2.contourArea(contour) > 0.5 * gray.size:
                rect = cv2.minAreaRect(contour)
                corners = cv2.boxPoints(rect).astype(np.float32)
                if (
                    min(rect[1]) > 100
                    and cv2.contourArea(contour) / max(1, rect[1][0] * rect[1][1]) > 0.85
                ):
                    sums = corners.sum(axis=1)
                    diff = np.diff(corners, axis=1)[:, 0]
                    corners = np.array(
                        [
                            corners[sums.argmin()],
                            corners[diff.argmin()],
                            corners[sums.argmax()],
                            corners[diff.argmax()],
                        ],
                        np.float32,
                    )
                    w = int(
                        max(
                            np.linalg.norm(corners[0] - corners[1]),
                            np.linalg.norm(corners[2] - corners[3]),
                        )
                    )
                    h = int(
                        max(
                            np.linalg.norm(corners[0] - corners[3]),
                            np.linalg.norm(corners[1] - corners[2]),
                        )
                    )
                    transform = cv2.getPerspectiveTransform(
                        corners,
                        np.array([[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], np.float32),
                    )
                    image = cv2.warpPerspective(image, transform, (w, h))
                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    corrected = True
                    warnings.append(("perspective_estimated", None))
            if not corrected:
                warnings.append(("perspective_skipped", None))
        bg = cv2.GaussianBlur(gray, (0, 0), 25)
        normalized = cv2.divide(gray, np.maximum(bg, 1), scale=255)
        normalized = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(normalized)
        # Remove colored ruling while preserving dark ink and dark crossing wires.
        b, g, r = cv2.split(image)
        ruling = ((b.astype(float) - r) > 25) | ((r.astype(float) - g) > 35)
        normalized[ruling & (gray > 130)] = 255
        image = cv2.cvtColor(normalized, cv2.COLOR_GRAY2BGR)
    if handwritten:
        warnings.append(("handwritten", None))
    return (
        image,
        warnings,
        (
            "handwritten"
            if handwritten
            else "printed"
            if style == "printed"
            else "photo"
            if photo
            else "printed"
        ),
    )


def figure_regions(image, components):
    """Recursively split broad horizontal/vertical gutters between circuit figures."""
    h, w = image.shape[:2]
    if len(components) < 4:
        return [(0, 0, w, h)]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def partition(box, cs, depth=0):
        x1, y1, x2, y2 = box
        if depth >= 4 or len(cs) < 4:
            return [box]
        roi = gray[y1:y2, x1:x2]
        candidates = []
        for axis in [0, 1]:
            projection = (roi < 150).sum(axis=axis)
            span = len(projection)
            cross = roi.shape[axis]
            blank = projection < max(2, cross * 0.003)
            start = None
            for k, empty in enumerate([*blank, False]):
                if empty and start is None:
                    start = k
                if not empty and start is not None:
                    if (
                        k - start > max(20, span * 0.035)
                        and start > span * 0.06
                        and k < span * 0.94
                    ):
                        cut = (start + k) // 2 + (x1 if axis == 0 else y1)
                        left = [c for c in cs if (c.bbox[axis] + c.bbox[axis + 2]) / 2 < cut]
                        right = [c for c in cs if c not in left]
                        if len(left) >= 2 and len(right) >= 2:
                            candidates.append((k - start, axis, cut, left, right))
                    start = None
        if not candidates:
            return [box]
        _, axis, cut, left, right = max(candidates, key=lambda c: c[0])
        a = (x1, y1, cut, y2) if axis == 0 else (x1, y1, x2, cut)
        b = (cut, y1, x2, y2) if axis == 0 else (x1, cut, x2, y2)
        return partition(a, left, depth + 1) + partition(b, right, depth + 1)

    return partition((0, 0, w, h), components)
