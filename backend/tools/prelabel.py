"""Prelabel to a NEW output directory; never edit the input collection."""

import argparse
import hashlib
import json
from pathlib import Path
import random
from ..domains.circuit.detect import detector


def main():
    p = argparse.ArgumentParser()
    p.add_argument("images")
    p.add_argument("--out", required=True)
    p.add_argument("--existing-labels")
    p.add_argument("--threshold", type=float, default=0.25)
    args = p.parse_args()
    from .eval_detector import iou

    model, cfg = detector()
    dest = Path(args.out)
    if dest.exists() and any(dest.iterdir()):
        p.error("Output must be new or empty")
    dest.mkdir(parents=True, exist_ok=True)
    records = []
    for path in sorted(Path(args.images).rglob("*")):
        if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        rows = []
        if args.existing_labels:
            existing = Path(args.existing_labels) / (path.stem + ".txt")
            if existing.exists():
                rows = existing.read_text(encoding="utf-8").splitlines()
        result = model.predict(
            str(path),
            imgsz=cfg["input_size"],
            conf=args.threshold,
            device="cpu",
            verbose=False,
        )[0]
        for b in result.boxes:
            cls = int(b.cls[0])
            x, y, w, h = b.xywhn[0].tolist()
            box = [x - w / 2, y - h / 2, x + w / 2, y + h / 2]
            duplicate = False
            for row in rows:
                k, cx, cy, bw, bh = map(float, row.split()[:5])
                if (
                    int(k) == cls
                    and iou(box, [cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2]) > 0.5
                ):
                    duplicate = True
                    break
            if not duplicate:
                rows.append(f"{cls} {x:.8f} {y:.8f} {w:.8f} {h:.8f}")
        (dest / (path.stem + ".txt")).write_text("\n".join(rows) + "\n")
        records.append(
            {
                "image": str(path),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "label": path.stem + ".txt",
                "human_reviewed": False,
            }
        )
    review = (
        random.Random(42).sample(records, min(len(records), max(10, len(records) // 10)))
        if records
        else []
    )
    (dest / "manifest.json").write_text(
        json.dumps(
            {"names": model.names, "records": records, "review_sample": review},
            indent=2,
        )
    )
    print(f"{len(records)} prelabels. All are unreviewed; inspect review_sample before training.")


if __name__ == "__main__":
    main()
