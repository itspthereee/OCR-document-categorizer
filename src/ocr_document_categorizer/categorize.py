from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .layout import Paragraph


@dataclass
class Section:
    heading: str
    text: str


def _is_heading(text: str) -> bool:
    if len(text) <= 3:
        return False
    if text.isupper():
        return True
    if text.endswith(":"):
        return True
    words = text.split()
    return len(words) <= 6 and all(word[0].isupper() for word in words if word)


def categorize_paragraphs(paragraphs: List[Paragraph]) -> List[Section]:
    sections: List[Section] = []
    current_heading = "Untitled"
    buffer: List[str] = []

    def flush():
        if buffer:
            sections.append(Section(heading=current_heading, text="\n".join(buffer)))
            buffer.clear()

    for paragraph in paragraphs:
        if _is_heading(paragraph.text.strip()):
            flush()
            current_heading = paragraph.text.strip().rstrip(":")
        else:
            buffer.append(paragraph.text.strip())

    flush()
    return sections
