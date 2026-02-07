from __future__ import annotations

import os
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

allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", "*").split(",")
    if origin.strip()
]
allow_credentials = "*" not in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

_reader: Optional[easyocr.Reader] = None


def _get_reader() -> easyocr.Reader:
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(["th", "en"], gpu=False)
    return _reader


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


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

        payload = {
            "lines": len(lines),
            "text": "\n".join(lines),
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
