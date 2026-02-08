from __future__ import annotations

import os
import re
from io import BytesIO
from pathlib import Path
from typing import Optional

import cv2
import easyocr
import numpy as np
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image

WEB_DIR = Path(__file__).parent / "web"

app = FastAPI(title="OCR Document Reader")

# CORS MUST be first - before any route mounts
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

_reader: Optional[easyocr.Reader] = None


def _get_reader() -> easyocr.Reader:
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["th", "en"], gpu=False, model_storage_dir='/tmp')
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


def _order_points(points: np.ndarray) -> np.ndarray:
    rect = np.zeros((4, 2), dtype="float32")
    s = points.sum(axis=1)
    rect[0] = points[np.argmin(s)]
    rect[2] = points[np.argmax(s)]

    diff = np.diff(points, axis=1)
    rect[1] = points[np.argmin(diff)]
    rect[3] = points[np.argmax(diff)]
    return rect


def _four_point_transform(image: np.ndarray, points: np.ndarray) -> np.ndarray:
    rect = _order_points(points)
    (top_left, top_right, bottom_right, bottom_left) = rect

    width_a = np.linalg.norm(bottom_right - bottom_left)
    width_b = np.linalg.norm(top_right - top_left)
    max_width = int(max(width_a, width_b))

    height_a = np.linalg.norm(top_right - bottom_right)
    height_b = np.linalg.norm(top_left - bottom_left)
    max_height = int(max(height_a, height_b))

    dst = np.array(
        [
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1],
        ],
        dtype="float32",
    )

    matrix = cv2.getPerspectiveTransform(rect, dst)
    return cv2.warpPerspective(image, matrix, (max_width, max_height))


def _try_crop_document(image: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 75, 200)

    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

    for contour in contours:
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
        if len(approx) == 4:
            return _four_point_transform(image, approx.reshape(4, 2).astype("float32"))

    return image


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

        cropped_image = _try_crop_document(image)

        reader = _get_reader()
        results = reader.readtext(cropped_image, detail=1)
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


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
