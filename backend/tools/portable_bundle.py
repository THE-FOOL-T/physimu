"""Build a source/model ZIP from tracked files, excluding each machine's private state."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile

from .check_models import ROOT, check_bundle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    failures = [row for row in check_bundle() if row["status"] != "OK"]
    if failures:
        raise SystemExit(f"Restore model files before packaging: {failures}")
    paths = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode("utf-8")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.out, "w", compression=ZIP_DEFLATED, compresslevel=6) as bundle:
        for relative in sorted(filter(None, paths.split("\0"))):
            if relative == "config.local.yaml" or ".venv" in Path(relative).parts:
                raise SystemExit("Private machine state is tracked; remove it before packaging")
            bundle.write(ROOT / relative, "circuit-sim/" + relative)
        bundle.writestr(
            "circuit-sim/BUNDLE_INFO.json",
            json.dumps({"source_commit": commit, "models": "models/manifest.json"}, indent=2),
        )
    with args.out.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    checksum = args.out.with_suffix(args.out.suffix + ".sha256")
    checksum.write_text(f"{digest}  {args.out.name}\n", encoding="utf-8")
    print(f"Created {args.out} ({args.out.stat().st_size:,} bytes)")
    print(f"SHA-256: {digest}")


if __name__ == "__main__":
    main()
