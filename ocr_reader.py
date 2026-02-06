"""EasyOCR wrapper utilities."""

from __future__ import annotations

from typing import Iterable, List

import easyocr


def create_reader(languages: Iterable[str] | None = None, *, gpu: bool = False) -> easyocr.Reader:
    """Create an EasyOCR Reader.

    Args:
        languages: Iterable of language codes like ["en"]. Defaults to ["en"].
        gpu: Whether to use GPU acceleration.
    """
    lang_list = list(languages) if languages else ["en"]
    return easyocr.Reader(lang_list, gpu=gpu)


def read_text(image_path: str, languages: Iterable[str] | None = None, *, gpu: bool = False) -> List[str]:
    """Read text from an image and return the detected strings."""
    reader = create_reader(languages, gpu=gpu)
    results = reader.readtext(image_path, detail=0)
    return list(results)
