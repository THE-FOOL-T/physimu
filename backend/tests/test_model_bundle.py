"""A downloaded pointer or damaged model must never pass the bundle preflight."""

import hashlib
import json

from circuit_sim.backend.tools.check_models import check_bundle


def test_bundle_preflight_distinguishes_missing_pointer_and_corruption(tmp_path):
    models = tmp_path / "models"
    models.mkdir()
    content = b"verified model"
    entries = []
    for name in ("valid", "missing", "pointer", "truncated", "changed"):
        entries.append(
            {
                "path": "models/" + name,
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
    (models / "manifest.json").write_text(json.dumps({"models": entries}), encoding="utf-8")
    (models / "valid").write_bytes(content)
    (models / "pointer").write_bytes(b"version https://git-lfs.github.com/spec/v1\noid sha256:abc")
    (models / "truncated").write_bytes(b"short")
    (models / "changed").write_bytes(b"corrupt! model")
    rows = check_bundle(tmp_path)
    assert rows[0]["status"] == "OK"
    assert rows[1]["status"].startswith("MISSING:")
    assert rows[2]["status"].startswith("LFS POINTER:")
    assert rows[3]["status"].startswith("WRONG SIZE:")
    assert rows[4]["status"].startswith("WRONG HASH:")
