"""Train a small nearest-centroid orientation/polarity classifier on known crops."""

import argparse
import json
from pathlib import Path
import cv2
import numpy as np
from ..pipeline.orientation import features


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--synthetic", required=True)
    p.add_argument(
        "--real-crops",
        help="Reviewed JSON list: image, orientation_deg, positive_first",
    )
    p.add_argument("--out", default="models/orientation.npz")
    args = p.parse_args()
    rows = []
    base = Path(args.synthetic)
    for path in (base / "netlists").glob("*.json"):
        net = json.loads(path.read_text(encoding="utf-8"))
        image = cv2.imread(str(base / "images" / (path.stem + ".png")))
        for c in net["components"]:
            if c["type"] not in {"dc_source", "battery", "ac_source"}:
                continue
            x, y, x2, y2 = [int(v) for v in c["bbox"]]
            crop = image[max(0, y) : y2, max(0, x) : x2]
            if not crop.size:
                continue
            angle = int(round(c["orientation_deg"] / 90)) % 4
            first = c["polarity"]["positive_terminal"] == c["terminals"][0]["id"]
            rows.append((features(crop), angle * 2 + (0 if first else 1)))
    real_count = 0
    if args.real_crops:
        for row in json.loads(Path(args.real_crops).read_text(encoding="utf-8")):
            if not row.get("human_reviewed"):
                p.error("Real crop labels must be reviewed")
            rows.append(
                (
                    features(cv2.imread(row["image"])),
                    (int(row["orientation_deg"]) // 90) * 2 + (0 if row["positive_first"] else 1),
                )
            )
            real_count += 1
    if not rows:
        p.error("No source crops")
    labels = sorted({label for _, label in rows})
    centroids = np.array([np.mean([x for x, y in rows if y == label], axis=0) for label in labels])
    np.savez(args.out, centroids=centroids, labels=np.array(labels))
    report = {
        "training_crops": len(rows),
        "real_training_crops": real_count,
        "classes": labels,
        "real_test_count": 0,
        "classifier_accuracy": None,
        "heuristic_accuracy": None,
        "enabled": False,
        "reason": "Independent orientation/polarity crop labels are required before replacing the heuristic.",
    }
    Path(args.out).with_suffix(".json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))


if __name__ == "__main__":
    main()
