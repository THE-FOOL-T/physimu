"""Run separately per CIRCUIT_THREADS setting; reports warmed local model stages."""

import argparse
import json
from pathlib import Path
import statistics
import time
import cv2
from ..inference import configure_threads
from ..pipeline.detect import detect
from ..pipeline.text import read_text, easy_reader


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", default="frontend/public/demos/mixed-network.png")
    parser.add_argument("--out", required=True)
    parser.add_argument("--count", type=int, default=3)
    args = parser.parse_args()
    started = time.perf_counter()
    threads = configure_threads()
    image = cv2.imread(args.image)
    if image is None:
        raise SystemExit("Unreadable profile image")
    detect(image)
    easy_reader("en")
    easy_reader("bn", False)
    warmup = time.perf_counter() - started
    rows = []
    for _ in range(args.count):
        start = time.perf_counter()
        components, _ = detect(image)
        detection = time.perf_counter() - start
        ocr_start = time.perf_counter()
        texts, warnings = read_text(image, components=components)
        rows.append(
            {
                "detect_seconds": detection,
                "ocr_seconds": time.perf_counter() - ocr_start,
                "readings": len(texts),
                "warnings": [code for code, _ in warnings],
            }
        )
    report = {
        "threads": threads,
        "warmup_seconds": warmup,
        "image": Path(args.image).name,
        "count": len(rows),
        "records": rows,
        "detect_median_seconds": statistics.median(r["detect_seconds"] for r in rows),
        "ocr_median_seconds": statistics.median(r["ocr_seconds"] for r in rows),
    }
    Path(args.out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report), flush=True)


if __name__ == "__main__":
    main()
