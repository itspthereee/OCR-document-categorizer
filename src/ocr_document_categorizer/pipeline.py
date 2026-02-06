from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np

from .categorize import Section, categorize_paragraphs
from .cropping import CropResult, crop_document
from .layout import group_lines_into_paragraphs
from .ocr import OCRLine, run_easyocr


@dataclass
class PipelineResult:
    crop: CropResult
    ocr_lines: List[OCRLine]
    sections: List[Section]


def load_image(path: Path) -> np.ndarray:
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(f"Could not read image: {path}")
    return image


def run_pipeline(image_path: Path, reader) -> PipelineResult:
    image = load_image(image_path)
    crop = crop_document(image)
    ocr_lines = run_easyocr(crop.cropped, reader)
    paragraphs = group_lines_into_paragraphs(ocr_lines)
    sections = categorize_paragraphs(paragraphs)
    return PipelineResult(crop=crop, ocr_lines=ocr_lines, sections=sections)
