"""In-process domain plugins. Selection is explicit; no automatic routing."""

from collections.abc import Callable
from typing import Any, Protocol


class Domain(Protocol):
    name: str
    stages: tuple[str, ...]

    def analyze(self, image: Any, options: dict, progress: Callable | None) -> dict: ...


_registry: dict[str, Domain] = {}


def register(domain: Domain) -> None:
    """Register once; accidental replacement of a loaded domain is an error."""
    if not domain.name or domain.name in _registry:
        raise ValueError(f"Duplicate or empty domain: {domain.name!r}")
    if not callable(domain.analyze):
        raise TypeError("Domain analyze must be callable")
    _registry[domain.name] = domain


def get(name: str) -> Domain:
    return _registry[name]


def names() -> tuple[str, ...]:
    return tuple(_registry)


from .circuit.adapter import CircuitDomain  # noqa: E402
from .mechanics import MechanicsDomain  # noqa: E402

register(CircuitDomain())
register(MechanicsDomain())

__all__ = ["Domain", "register", "get", "names"]
