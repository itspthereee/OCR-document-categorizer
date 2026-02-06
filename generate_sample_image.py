from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

out_path = Path("sample_heading_text.png")
width, height = 1400, 2000
img = Image.new("RGB", (width, height), "white")
draw = ImageDraw.Draw(img)

try:
    font_heading = ImageFont.truetype("DejaVuSans-Bold.ttf", 48)
    font_subheading = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
    font_body = ImageFont.truetype("DejaVuSans.ttf", 28)
except Exception:
    font_heading = ImageFont.load_default()
    font_subheading = ImageFont.load_default()
    font_body = ImageFont.load_default()

x, y = 60, 60
line_gap = 12

sections = [
    (
        "INVOICE",
        [
            "Invoice No: INV-2026-00042",
            "Date: 06 Feb 2026",
            "Customer: Acme Trading Co.",
            "Address: 123 Market Road, Bangkok 10110",
        ],
    ),
    (
        "BILL TO",
        [
            "Name: Somchai W.",
            "Email: somchai@example.com",
            "Phone: +66 80 123 4567",
        ],
    ),
    (
        "ITEMS",
        [
            "1. USB-C Hub — Qty: 2 — Unit: 450.00 — Total: 900.00",
            "2. Wireless Mouse — Qty: 1 — Unit: 520.00 — Total: 520.00",
            "3. Laptop Stand — Qty: 1 — Unit: 790.00 — Total: 790.00",
        ],
    ),
    (
        "PAYMENT SUMMARY",
        [
            "Subtotal: 2,210.00",
            "VAT (7%): 154.70",
            "Shipping: 50.00",
            "Total Due: 2,414.70",
            "Payment Method: PromptPay",
        ],
    ),
    (
        "NOTES",
        [
            "Please make payment within 7 days.",
            "For inquiries, contact billing@acme.co.th",
        ],
    ),
]

for title, lines in sections:
    draw.text((x, y), title, fill="black", font=font_heading)
    y += font_heading.size + line_gap

    for line in lines:
        draw.text((x + 20, y), line, fill="black", font=font_body)
        y += font_body.size + line_gap

    y += 30

footer_title = "TERMS & CONDITIONS"
draw.text((x, y), footer_title, fill="black", font=font_subheading)
y += font_subheading.size + line_gap

footer_lines = [
    "1. Goods sold are non-refundable after 7 days.",
    "2. Warranty covers manufacturing defects only.",
    "3. Late payment may incur additional fees.",
]
for line in footer_lines:
    draw.text((x + 20, y), line, fill="black", font=font_body)
    y += font_body.size + line_gap

img.save(out_path)
print(f"Wrote {out_path.resolve()}")
