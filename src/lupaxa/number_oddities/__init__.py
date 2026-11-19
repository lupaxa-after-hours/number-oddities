"""Offline inspector of recreational properties of integers."""

from lupaxa.number_oddities.properties import REGISTRY, evaluate, resolve
from lupaxa.number_oddities.version import __version__, get_version

__all__ = [
    "REGISTRY",
    "__version__",
    "evaluate",
    "get_version",
    "resolve",
]
