from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import numpy as np


@dataclass
class OCRLine:
    text: str
    bbox: List[Tuple[int, int]]
    confidence: float


def run_easyocr(image: np.ndarray, reader) -> List[OCRLine]:
    results = reader.readtext(image)
    lines: List[OCRLine] = []
    for bbox, text, conf in results:
        pts = [(int(x), int(y)) for x, y in bbox]
        lines.append(OCRLine(text=text, bbox=pts, confidence=float(conf)))
    return lines
