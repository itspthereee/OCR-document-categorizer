# OCR-document-categorizer

This project crops a document from a photo, runs OCR, and groups extracted text into topic headings.

## Features

- Auto-detect document boundaries and apply perspective correction.
- Extract text with `easyocr`.
- Group lines into paragraphs.
- Categorize paragraphs into headings using heuristics.
- Export structured JSON and plain text.

## Project structure

```
src/ocr_document_categorizer/
	cli.py
	pipeline.py
	cropping.py
	ocr.py
	layout.py
	categorize.py
	export.py
requirements.txt
```

## Setup

1. Install base dependencies:
   - `pip install -r requirements.txt`
   - or `pip install -e .`
2. Install EasyOCR separately (as requested):
   - `pip install easyocr`
   - or `pip install -e .[ocr]`

## Usage

```
ocr-doc-cat path/to/image.jpg \
	--lang en \
	--out-json output.json \
	--out-text output.txt
```

If you prefer running as a module:

```
python -m ocr_document_categorizer.cli path/to/image.jpg
```

## Desktop app

After installing dependencies (and EasyOCR), launch the desktop app:

```
ocr-doc-cat-desktop
```

Use the “Select Image” button, then “Run OCR”. The app shows the cropped document and categorized text.

### Desktop features

- Drag-and-drop image support (install optional dependency: `pip install -e .[desktop]`)
- Copy text button
- Export text as PDF

## Output

- `output.json` with sections and text.
- `output.txt` for quick editing.

## Notes

- Heading detection is heuristic-based (uppercase, trailing colon, or short title case). You can swap in a classifier later.
- If document detection fails, the original image is used for OCR.
