"""Write local mechanics proposals to a fresh folder. Every proposal is unreviewed."""

import argparse
import json
from pathlib import Path
import shutil

from PIL import Image

from .common import NAMES, FROZEN, contained, fresh, images, sha256, write_json, yolo_line
from .eval_detector import local_model, protocol


def propose(folder, weights, output, *, confidence=0.25, imgsz=640, device="cpu", model=None):
    source = Path(folder).resolve()
    if (
        source == FROZEN
        or source.is_relative_to(FROZEN)
        or contained(output).is_relative_to(source)
    ):
        raise ValueError("Do not prelabel frozen gold or write into the source collection")
    paths = images(folder)
    if not paths:
        raise ValueError("No images to prelabel")
    settings = protocol(imgsz, confidence)
    model = model or local_model(weights)
    out = fresh(output)
    (out / "images").mkdir()
    (out / "labels").mkdir()
    records = []
    for i, path in enumerate(paths):
        name = f"proposal_{i:04d}{path.suffix.lower()}"
        label = f"proposal_{i:04d}.txt"
        with Image.open(path) as image:
            w, h = image.size
        result = model.predict(
            str(path),
            imgsz=imgsz,
            conf=confidence,
            iou=0.7,
            max_det=300,
            device=device,
            save=False,
            verbose=False,
        )[0]
        lines = []
        for b in result.boxes:
            cls = int(b.cls[0])
            box = b.xyxy[0].tolist()
            box = [
                max(0, min(w, box[0])),
                max(0, min(h, box[1])),
                max(0, min(w, box[2])),
                max(0, min(h, box[3])),
            ]
            if box[0] < box[2] and box[1] < box[3]:
                lines.append(yolo_line(NAMES[cls], box, w, h))
        shutil.copyfile(path, out / "images" / name)
        (out / "labels" / label).write_text(
            "\n".join(lines) + ("\n" if lines else ""), encoding="utf-8"
        )
        records.append(
            {
                "image": f"images/{name}",
                "label": f"labels/{label}",
                "source_image": str(path.resolve()),
                "sha256": sha256(path),
                "label_sha256": sha256(out / "labels" / label),
                "human_reviewed": False,
            }
        )
    manifest = {
        "kind": "mechanics-proposals",
        "domain": "mechanics",
        "origin": "unreviewed",
        "class_names": list(NAMES),
        "weights_sha256": sha256(weights),
        "protocol": settings,
        "records": records,
    }
    write_json(out / "manifest.json", manifest)
    (out / "classes.txt").write_text("\n".join(NAMES) + "\n", encoding="utf-8")
    (out / "README.md").write_text(
        "# UNREVIEWED mechanics proposals\n\nImport YOLO boxes/images/classes into Label Studio, Roboflow or labelImg and review every box, including missing objects. Empty labels are proposals too. Export reviewed labels plus the explicit per-image review/source record described in docs/mechanics/labeling.md. This folder is rejected as a training dataset.\n",
        encoding="utf-8",
    )
    return manifest


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("images", type=Path)
    p.add_argument("--weights", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--confidence", type=float, default=0.25)
    p.add_argument("--device", default="cpu")
    a = p.parse_args()
    result = propose(
        a.images, a.weights, a.out, confidence=a.confidence, imgsz=a.imgsz, device=a.device
    )
    print(json.dumps({"images": len(result["records"]), "human_reviewed": False}))


if __name__ == "__main__":
    main()
