"""Read-only inventory of source assets; writes exclusively under circuit_sim."""

import collections
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import stat
import sys

ROOT = Path(__file__).resolve().parents[2]
os.environ.setdefault("YOLO_CONFIG_DIR", str(ROOT / ".cache" / "ultralytics"))


def main():
    import yaml
    from PIL import Image
    import torch

    torch.set_num_threads(1)
    from ultralytics import YOLO
    from ..config import load_config

    cfg = load_config()
    source = Path(cfg["detector"]["original"])
    target = ROOT / cfg["detector"]["weights"]
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copy2(source, target)
        target.chmod(stat.S_IREAD)

    def digest(p):
        return hashlib.sha256(p.read_bytes()).hexdigest()

    assert digest(source) == digest(target), "Weight copy differs; refusing overwrite"
    model = YOLO(str(target))
    inventory = []
    for base in [cfg["images"], cfg["additional_images"]]:
        paths = [
            p
            for p in Path(base).rglob("*")
            if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
        ]
        sizes = collections.Counter()
        for p in paths:
            with Image.open(p) as im:
                sizes[f"{im.width}x{im.height} {im.format}"] += 1
        parent = Path(base).parent
        inventory.append(
            {
                "path": base,
                "count": len(paths),
                "sizes": dict(sizes),
                "label_counts": {
                    e: len(list(parent.rglob("*." + e))) for e in ["txt", "json", "xml"]
                },
            }
        )
    samples = ROOT / "docs/recon_samples"
    samples.mkdir(parents=True, exist_ok=True)
    observations = []
    for p in sorted(Path(cfg["images"]).glob("*.png"))[:10]:
        r = model.predict(str(p), imgsz=640, conf=0.25, device="cpu", verbose=False)[0]
        r.save(str(samples / p.name))
        observations.append(
            {
                "image": p.name,
                "detections": len(r.boxes),
                "classes": dict(collections.Counter(model.names[int(c)] for c in r.boxes.cls)),
            }
        )
    environment = {
        "python": sys.version,
        "executable": sys.executable,
        "gpu": torch.cuda.is_available(),
        "packages": {d.metadata["Name"]: d.version for d in importlib.metadata.distributions()},
    }
    (ROOT / "docs/environment.json").write_text(json.dumps(environment, indent=2))
    record = {
        "weights": str(source),
        "copy": str(target),
        "sha256": digest(target),
        "task": model.task,
        "architecture": type(model.model).__name__,
        "names": model.names,
        "training_imgsz": model.overrides.get("imgsz"),
        "inference_imgsz": 640,
        "images": inventory,
        "samples": observations,
        "python": sys.version,
        "gpu": environment["gpu"],
    }
    (ROOT / "docs/recon.json").write_text(json.dumps(record, indent=2))
    (ROOT / "docs/recon.md").write_text(
        "# Asset reconnaissance\n\n"
        "Existing README and handoff read. Assets use the configured input paths. No source files changed.\n\n"
        "The original 59-image collection was used to TRAIN v2. Its historical evaluation directory name "
        "does not make it held-out data. The additional 99-image set has labels; independence must be checked "
        "against training manifests before using it as a frozen benchmark.\n\n"
        "Model and image inventory (observed, not assumed):\n\n```json\n"
        + json.dumps(record, indent=2)
        + "\n```\n\n"
        "Ten annotated predictions are in `recon_samples/`. Geometry/connectivity, source polarity and OCR "
        "are not detector outputs. Handwriting accuracy is unmeasured. See status.md for measured limitations.\n",
        encoding="utf-8",
    )
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
