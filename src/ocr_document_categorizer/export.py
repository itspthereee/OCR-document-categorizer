from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from .categorize import Section


def export_sections(sections: List[Section], output_path: Path) -> None:
    payload = {"sections": [asdict(section) for section in sections]}
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def export_plain_text(sections: List[Section], output_path: Path) -> None:
    lines = []
    for section in sections:
        lines.append(section.heading)
        lines.append(section.text)
        lines.append("")
    output_path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
