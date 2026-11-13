"""Geometric relationship candidates, independent of scene assembly and solvers."""

import numpy as np


def body_endpoints(points, bodies, reach=16.0):
    """Find observed trace points reaching each body's measured boundary.

    No endpoint is moved to a body solely because it is the nearest object.
    The returned gap remains available as evidence for ambiguous candidates.
    """
    ps = np.asarray(points, dtype=float)
    candidates = []
    for body in bodies:
        polygon = body["mask"]
        best = np.full(len(ps), np.inf)
        for a, b in zip(polygon, [*polygon[1:], polygon[0]]):
            a, b = np.asarray(a), np.asarray(b)
            d = b - a
            t = np.clip(((ps - a) @ d) / max(1e-9, d @ d), 0.0, 1.0)
            best = np.minimum(best, np.linalg.norm(ps - a - t[:, None] * d, axis=1))
        index = int(np.argmin(best))
        if best[index] <= reach:
            candidates.append(dict(body=body, point=ps[index].tolist(), gap=float(best[index])))
    return sorted(candidates, key=lambda r: (r["gap"], r["body"]["id"]))
