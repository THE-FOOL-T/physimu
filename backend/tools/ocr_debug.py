"""Inspect actual OCR, parsing and assignment; owner rasters stay gitignored."""

import argparse
import hashlib
import json
from pathlib import Path

import cv2

from ..domains.circuit.engine import analyze_page
from ..core.preprocess import decode

ROOT = Path(__file__).resolve().parents[2]


def debug_report(path, result):
    net = result["netlist"]
    return {
        "image": Path(path).name,
        "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        "diagnostics": result.get("diagnostics", {}),
        "components": [
            {key: c[key] for key in ["id", "type", "label", "bbox", "terminals", "value"]}
            for c in net["components"]
        ],
        "nodes": len(net["nodes"]),
        "provenance": result["provenance"],
        "warnings": result["warnings"],
        "timings": result["timings"],
        "nonzero_current": any(
            abs(r["current"]) > 1e-10 for r in result["solution"]["components"].values()
        ),
    }


def annotate(result, dest):
    import base64
    import numpy as np

    url = result.get("source_image", "")
    if not url.startswith("data:image/png;base64,"):
        return
    image = cv2.imdecode(
        np.frombuffer(base64.b64decode(url.split(",", 1)[1]), np.uint8),
        cv2.IMREAD_COLOR,
    )
    for c in result["netlist"]["components"]:
        x, y, x2, y2 = map(int, c["bbox"])
        cv2.rectangle(image, (x, y), (x2, y2), (180, 80, 20), 1)
        cv2.putText(
            image,
            c["id"],
            (x, max(12, y - 3)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (180, 80, 20),
            1,
        )
    for index, item in enumerate(result.get("diagnostics", {}).get("texts", [])):
        color = (
            (60, 150, 20)
            if item.get("outcome") == "assigned"
            else (0, 155, 230)
            if item.get("outcome") == "unassigned"
            else (150, 150, 150)
        )
        x, y, x2, y2 = map(int, item["bbox"])
        cv2.rectangle(image, (x, y), (x2, y2), color, 1)
        cv2.putText(
            image,
            str(index + 1),
            (x, max(10, y)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            color,
            1,
        )
    dest = Path(dest).resolve()
    if not dest.is_relative_to(ROOT):
        raise ValueError("Debug output must stay inside this repository")
    dest.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(dest), image)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image")
    parser.add_argument("--out", default=".cache/ocr-debug")
    args = parser.parse_args()
    path = Path(args.image)
    result = analyze_page(decode(path.read_bytes()))
    report = debug_report(path, result)
    out = Path(args.out).resolve()
    if not out.is_relative_to(ROOT):
        parser.error("Output must stay inside this repository")
    out.mkdir(parents=True, exist_ok=True)
    name = report["sha256"][:12]
    (out / (name + ".json")).write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    annotate(result, out / (name + ".png"))
    print(json.dumps(report, ensure_ascii=True, indent=2))
    print("Annotated PNG: " + str(out / (name + ".png")))


if __name__ == "__main__":
    main()
