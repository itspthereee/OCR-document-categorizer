"""Google Gemini Flash OCR utilities (google-genai SDK)."""

from __future__ import annotations

import json
import os


def _encode_image(image_path: str) -> bytes:
    """Read image file as raw bytes."""
    with open(image_path, "rb") as f:
        return f.read()


def _get_client():
    from google import genai

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")
    return genai.Client(api_key=api_key)


def read_and_categorize(image_path: str, languages: list | None = None) -> dict:
    """Read and categorize text from a document image using Gemini Flash.

    Returns a dict with keys:
      - text: full extracted text (str)
      - lines: line count (int)
      - categories: dict with header/items/amounts/footer lists
    """
    from google.genai import types

    client = _get_client()
    image_bytes = _encode_image(image_path)

    lang_hint = ""
    if languages:
        lang_hint = f" The document may contain text in: {', '.join(languages)}."

    prompt = (
        f"Analyze this document image.{lang_hint} "
        "Extract ALL text from the document, then categorize it into sections.\n"
        "Return ONLY a JSON object with this exact structure (no markdown, no explanation):\n"
        '{"text": "<full extracted text>", "categories": '
        '{"header": [], "items": [], "amounts": [], "footer": []}}\n\n'
        "Guidelines:\n"
        "- header: title, company/organization name, document type, date, reference numbers\n"
        "- items: products, services, line items, descriptions, quantities\n"
        "- amounts: prices, totals, subtotals, taxes, discounts\n"
        "- footer: notes, terms & conditions, contact info, signatures, stamps\n"
        "Each category is a list of strings (one entry per line/item)."
    )

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            prompt,
        ],
    )

    content = (response.text or "").strip()

    # Strip markdown code fences if the model wraps the response
    if content.startswith("```"):
        parts = content.split("```")
        for part in parts:
            stripped = part.lstrip("json").strip()
            if stripped.startswith("{"):
                content = stripped
                break

    try:
        result = json.loads(content)
        text = result.get("text", "")
        categories = result.get("categories", {})
        lines = [l for l in text.splitlines() if l.strip()]
        return {
            "text": text,
            "lines": len(lines),
            "categories": {
                "header": categories.get("header", []),
                "items": categories.get("items", []),
                "amounts": categories.get("amounts", []),
                "footer": categories.get("footer", []),
            },
        }
    except (json.JSONDecodeError, AttributeError):
        lines = [l for l in content.splitlines() if l.strip()]
        return {"text": content, "lines": len(lines)}
