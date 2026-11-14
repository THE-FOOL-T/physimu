"""Verify a configured local mechanics checkpoint, including its 21 classes."""

import json

from ...domains.mechanics.detect import checkpoint_readiness


def main():
    result = checkpoint_readiness(load=True)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
