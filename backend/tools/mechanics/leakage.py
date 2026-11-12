"""Mechanics split audit: source groups, exact hashes, near duplicates, frozen integrity."""

import argparse
import json
from pathlib import Path

from ...core import near, signature
from .common import FROZEN, load_dataset, relative_file, write_json, contained
from .gold import verify_frozen


def audit(manifest, root, frozen_root=FROZEN):
    root = Path(root).resolve()
    frozen = verify_frozen(frozen_root)
    frozen_signatures = [(row, signature(row["image"])) for row in frozen]
    records = manifest["records"]
    signatures = [(r, signature(relative_file(root, r["image"]))) for r in records]
    collisions, groups = [], {}
    for row, sig in signatures:
        group = row["source_group"]
        split = row["split"]
        if group in groups and groups[group] != split:
            collisions.append({"kind": "source_group_split", "group": group})
        groups[group] = split
        for other, fsig in frozen_signatures:
            if group == other["source_group"] or near(sig, fsig):
                collisions.append(
                    {
                        "kind": "frozen_overlap",
                        "image": row["image"],
                        "frozen": other["gold"],
                        "exact": sig[0] == fsig[0],
                    }
                )
    for i, (row, sig) in enumerate(signatures):
        for other, osig in signatures[:i]:
            if row["split"] != other["split"] and near(sig, osig):
                collisions.append(
                    {
                        "kind": "near_duplicate_split",
                        "image": row["image"],
                        "other": other["image"],
                        "exact": sig[0] == osig[0],
                    }
                )
    return {
        "passed": not collisions,
        "collisions": collisions,
        "images": len(records),
        "frozen_images": len(frozen),
        "frozen_styles": {
            style: sum(r["style"] == style for r in frozen) for style in ("printed", "handwritten")
        },
        "real_frozen_protection": "verified" if frozen else None,
        "human_task": None
        if frozen
        else "Frozen real gold is absent; this is a synthetic split audit only.",
        "method": "SHA256, source groups, and conservative dHash<=6 + binary Dice>0.92",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("dataset", type=Path)
    p.add_argument("--frozen", type=Path, default=FROZEN)
    p.add_argument("--out", type=Path)
    args = p.parse_args()
    result = audit(load_dataset(args.dataset), args.dataset, args.frozen)
    if args.out:
        write_json(contained(args.out), result)
    print(json.dumps(result, indent=2))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
