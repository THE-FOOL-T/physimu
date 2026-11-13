"""Seeded drawn glyphs and invertible smooth handwriting warp, with no learned assets."""

import math

import cv2
import numpy as np
from PIL import Image, ImageDraw


DIGITS = {
    "0": [
        [
            (0.5 + 0.34 * math.cos(t), 0.5 + 0.43 * math.sin(t))
            for t in np.linspace(0, 2 * math.pi, 25)
        ]
    ],
    "1": [[(0.22, 0.25), (0.52, 0.08), (0.52, 0.92)], [(0.25, 0.92), (0.75, 0.92)]],
    "2": [
        [
            (0.12, 0.25),
            (0.22, 0.1),
            (0.62, 0.08),
            (0.82, 0.25),
            (0.78, 0.42),
            (0.12, 0.92),
            (0.87, 0.92),
        ]
    ],
    "3": [
        [
            (0.12, 0.12),
            (0.68, 0.08),
            (0.82, 0.25),
            (0.65, 0.45),
            (0.38, 0.48),
            (0.7, 0.5),
            (0.84, 0.72),
            (0.7, 0.9),
            (0.18, 0.92),
        ]
    ],
    "4": [[(0.62, 0.08), (0.12, 0.62), (0.88, 0.62)], [(0.67, 0.08), (0.67, 0.95)]],
    "5": [
        [
            (0.85, 0.1),
            (0.24, 0.1),
            (0.18, 0.48),
            (0.65, 0.45),
            (0.84, 0.63),
            (0.8, 0.83),
            (0.58, 0.94),
            (0.12, 0.87),
        ]
    ],
    "6": [
        [
            (0.76, 0.1),
            (0.44, 0.13),
            (0.22, 0.35),
            (0.16, 0.72),
            (0.28, 0.9),
            (0.66, 0.92),
            (0.83, 0.72),
            (0.72, 0.5),
            (0.34, 0.48),
            (0.17, 0.67),
        ]
    ],
    "7": [[(0.1, 0.1), (0.9, 0.1), (0.33, 0.94)]],
    "8": [
        [
            (0.5 + 0.34 * math.sin(t), 0.5 + 0.43 * math.sin(2 * t))
            for t in np.linspace(0, 2 * math.pi, 40)
        ]
    ],
    "9": [
        [
            (0.8, 0.43),
            (0.63, 0.12),
            (0.3, 0.1),
            (0.12, 0.3),
            (0.23, 0.5),
            (0.6, 0.53),
            (0.8, 0.39),
            (0.75, 0.7),
            (0.52, 0.92),
            (0.22, 0.93),
        ]
    ],
    "-": [[(0.15, 0.5), (0.85, 0.5)]],
    "+": [[(0.15, 0.5), (0.85, 0.5)], [(0.5, 0.15), (0.5, 0.85)]],
    "=": [[(0.15, 0.35), (0.85, 0.35)], [(0.15, 0.65), (0.85, 0.65)]],
    "/": [[(0.15, 0.95), (0.8, 0.05)]],
    "°": [
        [
            (0.5 + 0.23 * math.cos(t), 0.22 + 0.2 * math.sin(t))
            for t in np.linspace(0, 2 * math.pi, 20)
        ]
    ],
}


def label_mask(text, font, rng):
    """Draw Latin digits/symbols as pen paths; jitter local-font unit/Bangla glyphs."""
    size = font.size
    result = Image.new("L", (math.ceil(sum(font.getlength(c) + 3 for c in text)) + size, size * 3))
    cursor = 3
    for char in text:
        width = max(4, math.ceil(font.getlength(char)))
        glyph = Image.new("L", (width + 8, size + 8))
        draw = ImageDraw.Draw(glyph)
        if char in DIGITS:
            for path in DIGITS[char]:
                points = [
                    (
                        3 + x * width + rng.uniform(-0.45, 0.45),
                        3 + y * size + rng.uniform(-0.45, 0.45),
                    )
                    for x, y in path
                ]
                draw.line(points, fill=255, width=rng.choice([1, 1, 2]), joint="curve")
        else:
            draw.text((3, 3), char, font=font, anchor="lt", fill=255, stroke_width=0)
        glyph = glyph.rotate(rng.uniform(-7, 7), resample=Image.Resampling.BICUBIC, expand=False)
        result.paste(glyph, (cursor, rng.randint(0, 2)), glyph)
        cursor += width + rng.randint(0, 2)
    return result.crop(result.getbbox()) if result.getbbox() else result


def elastic_parameters(rng):
    return dict(
        amplitude_px=[rng.uniform(1.0, 2.8), rng.uniform(1.0, 2.8)],
        period_px=[rng.uniform(170, 290), rng.uniform(170, 290)],
        phase_rad=[rng.uniform(0, 2 * math.pi), rng.uniform(0, 2 * math.pi)],
        inverse_iterations=8,
    )


def deform(points, settings):
    points = np.asarray(points, dtype=np.float64)
    a, b = settings["amplitude_px"]
    px, py = settings["period_px"]
    u, v = settings["phase_rad"]
    return points + np.stack(
        [
            a * np.sin(points[..., 1] * 2 * np.pi / py + u),
            b * np.sin(points[..., 0] * 2 * np.pi / px + v),
        ],
        axis=-1,
    )


def inverse_maps(width, height, settings):
    y, x = np.mgrid[:height, :width].astype(np.float32)
    destination = np.stack([x, y], axis=-1)
    source = destination.copy()
    for _ in range(settings["inverse_iterations"]):
        source = destination - (deform(source, settings) - source)
    return source[..., 0].astype(np.float32), source[..., 1].astype(np.float32)


def warp(array, maps, *, mask=False, border=(255, 255, 255)):
    return cv2.remap(
        array,
        *maps,
        cv2.INTER_NEAREST if mask else cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=0 if mask else border,
    )


def notebook(image, rng):
    """Background ruling/shadows do not become object labels."""
    array = np.array(image, dtype=np.float32)
    h, w = array.shape[:2]
    spacing = rng.randint(23, 35)
    phase = rng.randrange(spacing)
    for y in range(phase, h, spacing):
        # Only light paper changes; dark diagram ink remains intact.
        keep = np.min(array[y], axis=1) > 180
        array[y, keep] = np.minimum(array[y, keep], [193, 209, 230])
    x = np.linspace(0, 1, w)[None, :]
    centre = rng.uniform(0.1, 0.9)
    shadow = 1 - rng.uniform(0.07, 0.16) * np.exp(-(((x - centre) / 0.18) ** 2))
    array *= shadow[..., None]
    return Image.fromarray(np.uint8(np.clip(array, 0, 255))), dict(
        spacing_px=spacing, phase_px=phase
    )
