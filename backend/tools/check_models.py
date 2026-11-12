"""Check the portable model bundle without importing ML libraries or downloading files."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LFS_HEADER = b"version https://git-lfs.github.com/spec/v1"


def check_bundle(root=ROOT):
    manifest = json.loads((root / "models/manifest.json").read_text(encoding="utf-8"))
    results = []
    for model in manifest["models"]:
        path = root / model["path"]
        if not path.is_file():
            status = "MISSING: restore the complete bundle or run git lfs pull"
        else:
            with path.open("rb") as stream:
                pointer = stream.read(len(LFS_HEADER)) == LFS_HEADER
            if pointer:
                status = "LFS POINTER: run git lfs install, then git lfs pull"
            elif path.stat().st_size != model["bytes"]:
                status = "WRONG SIZE: incomplete or different model; restore the bundle"
            else:
                with path.open("rb") as stream:
                    digest = hashlib.file_digest(stream, "sha256").hexdigest()
                status = (
                    "OK"
                    if digest == model["sha256"]
                    else "WRONG HASH: different model; restore the bundle"
                )
        results.append({"path": model["path"], "status": status})
    return results


def main():
    results = check_bundle()
    for row in results:
        print(f"{row['status']}  {row['path']}")
    if any(row["status"] != "OK" for row in results):
        raise SystemExit(1)
    print("All five bundled models match. Start the server and check /api/health for readiness.")
    print("Private config.local.yaml and CIRCUIT_* environment variables override bundle defaults.")


if __name__ == "__main__":
    main()
