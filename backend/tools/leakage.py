"""Exact and conservative near-duplicate checks for frozen detector evaluation."""

import hashlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps


def signature(path):
    with Image.open(path) as im:
        gray = ImageOps.exif_transpose(im).convert("L")
        tiny = np.array(gray.resize((9, 8)), dtype=int)
        bits = (tiny[:, 1:] > tiny[:, :-1]).ravel()
        dhash = sum(int(bit) << i for i, bit in enumerate(bits))
        raster = np.array(gray.resize((64, 64)))
    return hashlib.sha256(Path(path).read_bytes()).hexdigest(), dhash, raster < 180


def near(a, b):
    if a[0] == b[0]:
        return True
    if (a[1] ^ b[1]).bit_count() > 6:
        return False
    total = int(a[2].sum() + b[2].sum())
    return total > 8 and 2 * int((a[2] & b[2]).sum()) / total > 0.92


def check_frozen(training, test):
    frozen = [(p, signature(p)) for p in test]
    collisions = []
    for path in training:
        sig = signature(path)
        for target, other in frozen:
            if near(sig, other):
                collisions.append(
                    {
                        "training": str(path),
                        "test": str(target),
                        "exact": sig[0] == other[0],
                    }
                )
    return collisions


def balanced_records(records):
    """Oversample real train images so synthetic share never exceeds one half."""
    real = [r for r in records if not r["synthetic"]]
    synthetic = [r for r in records if r["synthetic"]]
    if not real:
        raise ValueError("A training mix requires real images")
    if len(real) < len(synthetic):
        real = (real * ((len(synthetic) + len(real) - 1) // len(real)))[: len(synthetic)]
    return real + synthetic


def duplicate_groups(paths):
    signatures = [signature(p) for p in paths]
    parent = list(range(len(paths)))

    def root(i):
        while parent[i] != i:
            i = parent[i]
        return i

    for i in range(len(paths)):
        for j in range(i):
            if near(signatures[i], signatures[j]):
                parent[root(i)] = root(j)
    return {str(path): root(i) for i, path in enumerate(paths)}
