# OCR-document-categorizer

Develop a program that can crop documents and read the text within them, outputting the content as editable text, while categorizing the text into desired topic headings.

## EasyOCR

This branch includes EasyOCR integration.

Install dependencies:

    pip install -r requirements.txt

Quick usage:

    from ocr_reader import read_text

    text_lines = read_text("/path/to/image.jpg")
