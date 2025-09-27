"""Simple web crawler package."""

from importlib import import_module
from typing import TYPE_CHECKING, Any

__all__ = ["crawler", "dashboard", "portal"]

if TYPE_CHECKING:  # pragma: no cover - imported for type checkers only
    from . import portal as portal  # noqa: F401  (re-exported name)


def __getattr__(name: str) -> Any:
    if name == "portal":
        module = import_module(".portal", __name__)
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
