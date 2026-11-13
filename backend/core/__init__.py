"""Stable shared facade backed by local core implementations."""

from .config import load_config
from .preprocess import MAX_BYTES, decode, figure_regions, preprocess
from .style import estimate_style
from .text import read_text
from .images import image_url
from .jobs import Cancelled, JobStore, STAGES
from .leakage import check_frozen, duplicate_groups, signature, near
from .inference import configure_threads
from .value_tokens import DIGITS as OCR_DIGITS
from .ocr_tiles import windows as ocr_windows
from .ocr_regions import anchored_regions, crop_variants
from .models import model_lease, register_model_release
from .label_reader import CropLabelReader

__all__ = [
    "load_config",
    "MAX_BYTES",
    "decode",
    "figure_regions",
    "preprocess",
    "estimate_style",
    "read_text",
    "image_url",
    "Cancelled",
    "JobStore",
    "STAGES",
    "check_frozen",
    "duplicate_groups",
    "signature",
    "near",
    "configure_threads",
    "OCR_DIGITS",
    "ocr_windows",
    "anchored_regions",
    "crop_variants",
    "model_lease",
    "register_model_release",
    "CropLabelReader",
]
