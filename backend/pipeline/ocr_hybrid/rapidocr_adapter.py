"""Compatibility alias; implementation moved in M7."""

from importlib import import_module as _import_module
import sys as _sys

_sys.modules[__name__] = _import_module("...core.ocr_hybrid.rapidocr_adapter", __package__)
