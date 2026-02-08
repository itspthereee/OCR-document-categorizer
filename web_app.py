from __future__ import annotations

import io
import os

import google.generativeai as genai
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

app = FastAPI(title="OCR Document Reader")

# CORS for all domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_model: genai.GenerativeModel | None = None
_model_name: str | None = None

def _select_model_name() -> str:
    # Allow override from environment; try a few known model names as fallback.
    env_model = os.environ.get("GEMINI_MODEL")
    if env_model:
        return env_model
    # Order matters: newest/most available first.
    return "gemini-1.5-flash-latest"


def _get_model() -> genai.GenerativeModel:
    global _model, _model_name
    if _model is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        genai.configure(api_key=api_key)
        # Use the model name expected by the GenAI client (no models/ prefix).
        _model_name = _select_model_name()
        _model = genai.GenerativeModel(_model_name)
    return _model


@app.post("/api/ocr")
async def ocr_endpoint(file: UploadFile = File(...)) -> dict:
    if file.content_type is None or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    try:
        image_data = await file.read()
        if not image_data:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        image = Image.open(io.BytesIO(image_data))
        prompt = "อ่านข้อความในรูปนี้และสรุปแยกหมวดหมู่เอกสารให้หน่อย (Output as text)"
        try:
            response = _get_model().generate_content([prompt, image])
        except Exception as exc:  # noqa: BLE001
            # Provide a clearer error for missing/unsupported model names.
            detail = str(exc)
            if "not found" in detail or "ListModels" in detail:
                raise HTTPException(
                    status_code=500,
                    detail=(
                        "Model not available for this API key. "
                        "Set GEMINI_MODEL to a valid model name for your account. "
                        f"Current model: {_model_name}"
                    ),
                ) from exc
            raise
        text = response.text or ""
        lines = [line for line in text.splitlines() if line.strip()]
        return {"text": text, "lines": len(lines)}
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)
