from __future__ import annotations

import argparse
from pathlib import Path

import easyocr

from .export import export_plain_text, export_sections
from .pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OCR document categorizer")
    parser.add_argument("image", type=Path, help="Path to input image")
    parser.add_argument("--lang", nargs="+", default=["en"], help="OCR languages")
    parser.add_argument("--out-json", type=Path, default=Path("output.json"))
    parser.add_argument("--out-text", type=Path, default=Path("output.txt"))
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    reader = easyocr.Reader(args.lang)
    result = run_pipeline(args.image, reader)

    export_sections(result.sections, args.out_json)
    export_plain_text(result.sections, args.out_text)


if __name__ == "__main__":
    main()
