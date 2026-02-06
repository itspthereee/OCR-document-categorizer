from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .ocr import OCRLine


@dataclass
class Paragraph:
    text: str
    line_indices: List[int]


def _line_center_y(line: OCRLine) -> float:
    ys = [pt[1] for pt in line.bbox]
    return sum(ys) / len(ys)


def group_lines_into_paragraphs(lines: List[OCRLine], y_threshold: int = 18) -> List[Paragraph]:
    if not lines:
        return []

    sorted_indices = sorted(range(len(lines)), key=lambda i: _line_center_y(lines[i]))
    paragraphs: List[Paragraph] = []
    current: List[int] = [sorted_indices[0]]

    for idx in sorted_indices[1:]:
        prev_idx = current[-1]
        if abs(_line_center_y(lines[idx]) - _line_center_y(lines[prev_idx])) <= y_threshold:
            current.append(idx)
        else:
            text = " ".join(lines[i].text for i in current)
            paragraphs.append(Paragraph(text=text, line_indices=current))
            current = [idx]

    text = " ".join(lines[i].text for i in current)
    paragraphs.append(Paragraph(text=text, line_indices=current))
    return paragraphs
