from __future__ import annotations

import os
import re
from io import BytesIO
from pathlib import Path
from typing import Optional

import easyocr
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image

WEB_DIR = Path(__file__).parent / "web"

app = FastAPI(title="OCR Document Reader")
app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

# CORS Configuration - Allow all origins for API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # อนุญาตทุก origin
    allow_credentials=False,  # ต้องเป็น False เมื่อใช้ allow_origins=["*"]
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight request เป็นเวลา 1 ชั่วโมง
)

_reader: Optional[easyocr.Reader] = None


def _get_reader() -> easyocr.Reader:
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["th", "en"], gpu=False)
    return _reader


def _categorize_text(text: str) -> dict:
    """Categorize extracted text into sections."""
    lines = text.split("\n")
    categories = {
        "header": [],
        "items": [],
        "amounts": [],
        "footer": [],
    }
    
    # Keywords for categorization
    header_keywords = [r"invoice|receipt|bill|เอกสาร|ใบเสร็จ|ใบแจ้ง|ชื่อ|ที่อยู่|address"]
    item_keywords = [r"product|item|description|รายการ|สินค้า|ชื่อสินค้า|qty|quantity"]
    amount_keywords = [r"price|amount|total|subtotal|tax|discount|ราคา|รวม|ส่วนลด|ภาษี|มูลค่า"]
    
    for line in lines:
        line_lower = line.lower()
        
        # Check if line contains amount/price/total info
        if any(re.search(pattern, line_lower) for pattern in amount_keywords):
            categories["amounts"].append(line.strip())
        # Check if line contains item info
        elif any(re.search(pattern, line_lower) for pattern in item_keywords):
            categories["items"].append(line.strip())
        # Check if line contains header info
        elif any(re.search(pattern, line_lower) for pattern in header_keywords):
            categories["header"].append(line.strip())
        # Remaining lines go to footer
        elif line.strip():
            categories["footer"].append(line.strip())
    
    return categories


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")
@app.get("/styles.css")
def styles() -> FileResponse:
    return FileResponse(WEB_DIR / "styles.css", media_type="text/css")


@app.get("/app.js")
def app_js() -> FileResponse:
    return FileResponse(WEB_DIR / "app.js", media_type="application/javascript")




@app.post("/api/ocr")
def run_ocr(file: UploadFile = File(...)) -> JSONResponse:
    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    try:
        image_bytes = file.file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        pil_image = Image.open(BytesIO(image_bytes)).convert("RGB")
        image = np.array(pil_image)

        reader = _get_reader()
        results = reader.readtext(image, detail=1)
        lines = [text for _, text, _ in results]
        full_text = "\n".join(lines)
        
        # Categorize the extracted text
        categories = _categorize_text(full_text)

        payload = {
            "lines": len(lines),
            "text": full_text,
            "categories": categories,
        }
        return JSONResponse(payload)
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


def main() -> None:
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("web_app:app", host="0.0.0.0", port=port, reload=False)


if __name__ == "__main__":
    main()
