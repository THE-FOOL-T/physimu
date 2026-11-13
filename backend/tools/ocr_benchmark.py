"""Measured small-label regression, using installed local EasyOCR models only."""

import json
import time
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ..core.text import easy_reader
from ..core.ocr_tiles import easy_tiles
from ..domains.circuit.values import normalize

ROOT = Path(__file__).resolve().parents[2]
LABELS = ["4 Ω", "12 V", "2.2 kΩ", "100 µF", "২Ω", "R₁"]


def compact(text):
    return normalize(text).replace(" ", "").lower()


def main():
    try:
        reader = easy_reader("en")
        easy_reader("bn", False)
    except Exception as exc:
        result = {
            "before_recall": None,
            "after_recall": None,
            "error": type(exc).__name__,
        }
    else:
        rows = []
        import matplotlib

        latin = Path(matplotlib.get_data_path()) / "fonts/ttf/DejaVuSans.ttf"
        for height in (10, 12, 14):
            page = Image.new("RGB", (1800, 1800), "white")
            draw = ImageDraw.Draw(page)
            for i, label in enumerate(LABELS):
                size = 32

                def fonts(size):
                    return [
                        ImageFont.truetype(
                            str(ROOT / "frontend/public/fonts/NotoSansBengali.ttf")
                            if "\u0980" <= char <= "\u09ff"
                            else str(latin),
                            size,
                        )
                        for char in label
                    ]

                while size > 6:
                    glyph_fonts = fonts(size)
                    if (
                        max(f.getbbox(c)[3] - f.getbbox(c)[1] for c, f in zip(label, glyph_fonts))
                        <= height
                    ):
                        break
                    size -= 1
                x = 80 + (i % 2) * 900
                y = 220 + (i // 2) * 500
                for char, font in zip(label, glyph_fonts):
                    draw.text((x, y), char, font=font, fill="black", anchor="ls")
                    x += draw.textlength(char, font=font)
            image = cv2.cvtColor(np.asarray(page), cv2.COLOR_RGB2BGR)
            start = time.perf_counter()
            factor = 640 / 1800
            before = reader.readtext(
                cv2.resize(image, None, fx=factor, fy=factor),
                canvas_size=640,
                detail=1,
                paragraph=False,
                batch_size=1,
            )
            before_seconds = time.perf_counter() - start
            start = time.perf_counter()
            after = easy_tiles(image, reader, lambda: easy_reader("bn", False))
            after_seconds = time.perf_counter() - start
            before_text = [r[1] for r in before]
            after_text = [r["text"] for r in after]
            for label in LABELS:
                rows.append(
                    {
                        "height": height,
                        "label": label,
                        "before": any(compact(label) == compact(s) for s in before_text),
                        "after": any(compact(label) == compact(s) for s in after_text),
                    }
                )
            rows.append(
                {
                    "height": height,
                    "before_seconds": before_seconds,
                    "after_seconds": after_seconds,
                    "before_text": before_text,
                    "after_text": after_text,
                }
            )
            print(
                json.dumps(
                    {
                        "height": height,
                        "before_seconds": before_seconds,
                        "after_seconds": after_seconds,
                    }
                ),
                flush=True,
            )
        labels = [r for r in rows if "label" in r]
        result = {
            "samples": len(labels),
            "before_recall": sum(r["before"] for r in labels) / len(labels),
            "after_recall": sum(r["after"] for r in labels) / len(labels),
            "rows": rows,
            "scope": "Exact normalized string recall; 640 px English baseline vs native tiled EN + ambiguous BN refinement; warm local CPU, no downloads. Synthetic typography, not handwritten accuracy.",
        }
    (ROOT / "docs/ocr_benchmark.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return result


if __name__ == "__main__":
    main()
