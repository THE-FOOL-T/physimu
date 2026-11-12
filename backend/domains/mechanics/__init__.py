"""M1 placeholder. No extraction, assumed scene, solver, or circuit fallback."""

from ...core import image_url


class MechanicsDomain:
    name = "mechanics"
    stages = ("received", "done")

    def analyze(self, image, options: dict, progress=None) -> dict:
        return {
            "domain": self.name,
            "provenance": "unsupported",
            "reason": "not_implemented",
            "scene": {},
            "warnings": [{"code": "not_implemented", "ref": None, "message_key": "mech.pending"}],
            "timings": {},
            "source_image": image_url(image),
            "style_estimate": {},
        }
