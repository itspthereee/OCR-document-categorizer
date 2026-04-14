"""Google Gemini Flash OCR — direct REST API (no SDK)."""

from __future__ import annotations

import base64
import json
import os

import requests


def _encode_image(image_path: str) -> str:
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def read_and_categorize(image_path: str, languages: list | None = None) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    image_data = _encode_image(image_path)

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

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={api_key}"
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"inline_data": {"mime_type": "image/png", "data": image_data}},
                    {"text": prompt},
                ]
            }
        ]
    }

    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()

    content = (
        resp.json()
        .get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
        .strip()
    )

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
