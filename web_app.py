from __future__ import annotations

import io
import os
import tempfile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from ocr_reader import read_text

app = FastAPI(title="OCR Document Reader")

# CORS for all domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/api/ocr")
async def ocr_endpoint(
    file: UploadFile = File(...),
    languages: str | None = Form(None),
) -> dict:
    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    try:
        image_data = await file.read()
        if not image_data:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        image = Image.open(io.BytesIO(image_data))
        image.load()

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            temp_path = tmp.name
            image.save(tmp, format="PNG")

        lang_list = None
        if languages:
            lang_list = [lang.strip() for lang in languages.split(",") if lang.strip()]
        
        if not lang_list:
            lang_list = ["th", "en"]

        try:
            lines = read_text(temp_path, languages=lang_list)
        finally:
            try:
                os.remove(temp_path)
            except OSError:
                pass

        return {"text": "\n".join(lines), "lines": len(lines)}
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
