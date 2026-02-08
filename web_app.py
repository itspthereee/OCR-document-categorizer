from __future__ import annotations

import io
import os

import google.generativeai as genai
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
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


def _list_available_models() -> list[str]:
    """List all available Gemini models for the configured API key."""
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return []
        genai.configure(api_key=api_key)
        models = genai.list_models()
        return [m.name.replace("models/", "") for m in models if "generateContent" in m.supported_generation_methods]
    except Exception:
        return []


def _select_model_name() -> str:
    """Select the best available model name."""
    env_model = os.environ.get("GEMINI_MODEL")
    if env_model:
        return env_model
    
    # Try to find an available flash model
    available = _list_available_models()
    
    # Preferred models in order
    preferred = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-002",
        "gemini-1.5-flash-8b",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro",
        "gemini-pro-vision",
    ]
    
    for model in preferred:
        if model in available:
            return model
    
    # Fallback: use any flash model available
    for model in available:
        if "flash" in model.lower():
            return model
    
    # Last resort: use the first available model
    if available:
        return available[0]
    
    # Default fallback (will likely fail but gives clear error)
    return "gemini-1.5-flash"


def _get_model() -> genai.GenerativeModel:
    global _model, _model_name
    if _model is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")
        genai.configure(api_key=api_key)
        _model_name = _select_model_name()
        _model = genai.GenerativeModel(_model_name)
    return _model


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the frontend HTML."""
    html_path = os.path.join(os.path.dirname(__file__), "web", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>OCR Document Reader API</h1><p>Upload to /api/ocr</p>"


@app.get("/{filename}")
async def serve_static(filename: str):
    """Serve static files from web folder."""
    web_path = os.path.join(os.path.dirname(__file__), "web", filename)
    if os.path.exists(web_path) and filename in ["app.js", "styles.css"]:
        with open(web_path, "r", encoding="utf-8") as f:
            content = f.read()
        if filename.endswith(".js"):
            from fastapi.responses import Response
            return Response(content=content, media_type="application/javascript")
        elif filename.endswith(".css"):
            from fastapi.responses import Response
            return Response(content=content, media_type="text/css")
    raise HTTPException(status_code=404, detail="File not found")


@app.get("/api/health")
async def health_check() -> dict:
    """Health check endpoint that shows API status and available models."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "status": "error",
            "message": "GEMINI_API_KEY not configured",
            "available_models": [],
        }
    
    try:
        available = _list_available_models()
        selected = _select_model_name()
        return {
            "status": "ok",
            "selected_model": selected,
            "available_models": available,
            "model_count": len(available),
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "available_models": [],
        }


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
            model = _get_model()
            response = model.generate_content([prompt, image])
        except Exception as exc:  # noqa: BLE001
            # Provide a clearer error for missing/unsupported model names.
            detail = str(exc)
            available = _list_available_models()
            if "not found" in detail.lower() or "listmodels" in detail.lower() or "404" in detail:
                raise HTTPException(
                    status_code=500,
                    detail=(
                        f"Model '{_model_name}' not available. "
                        f"Available models: {', '.join(available) if available else 'none'}. "
                        "Set GEMINI_MODEL environment variable to a valid model name."
                    ),
                ) from exc
            raise HTTPException(status_code=500, detail=f"Gemini API error: {detail}") from exc
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
