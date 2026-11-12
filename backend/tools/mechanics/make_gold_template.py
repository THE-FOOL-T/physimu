"""Make an unreviewed human scaffold outside frozen folders; never create a gold scene."""

import argparse
import shutil
from pathlib import Path

from .common import fresh, sha256, write_json


def make_template(image, output):
    image = Path(image).resolve(strict=True)
    dest = fresh(output)
    shutil.copyfile(image, dest / image.name)
    template = {
        "kind": "mechanics-human-gold",
        "version": 1,
        "source": {
            "image": image.name,
            "sha256": sha256(image),
            "group": "",
            "reference": "",
            "licence_note": "HUMAN decision required",
        },
        "review": {"human_reviewed": False, "reviewer": "", "reviewed_at": "", "notes": ""},
        "scene": None,
    }
    write_json(dest / "human-template.json", template)
    (dest / "README.md").write_text(
        "# HUMAN scaffold — NOT GOLD\n\nScene is intentionally null. Author in the Mechanics editor; "
        "export the portable project and copy its canonical source scene here after independent "
        "review. Fill source/group/licence/review fields yourself. Only a person can designate "
        "reviewed gold and place it in the frozen tree.\n",
        encoding="utf-8",
    )
    return template


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("image", type=Path)
    p.add_argument("--out", required=True, type=Path)
    args = p.parse_args()
    make_template(args.image, args.out)
    print("Wrote a null-scene human scaffold, outside frozen gold.")


if __name__ == "__main__":
    main()
