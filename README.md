# OCR-document-categorizer

Simple OCR web app using Google Gemini AI with a drag-and-drop frontend.

## Features

-  Extract and categorize text from images
-  Powered by Google Gemini AI (gemini-1.5-flash)
-  Automatic model selection with fallback
-  Built-in web interface
-  Health check endpoint

## Quick Start

### 1. Get a Gemini API Key

Get your free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

### 2. Test Locally

```bash
# Set your API key
$env:GEMINI_API_KEY = "your-api-key-here"

# Install dependencies
pip install -r requirements.txt

# Test API connection (optional but recommended)
python test_gemini.py

# Run the server
python web_app.py
```

Open http://localhost:8000

### 3. Deploy to Koyeb/Render

**Environment Variables:**
- `GEMINI_API_KEY` (required) - Your Google AI API key
- `GEMINI_MODEL` (optional) - Specific model name (default: auto-select)
- `PORT` (optional) - Server port (default: 8000)

**Build & Start:**
- Build: `pip install -r requirements.txt`
- Start: `uvicorn web_app:app --host 0.0.0.0 --port $PORT`

See [DEPLOY.md](DEPLOY.md) for detailed deployment instructions.

## API Endpoints

- `GET /` - Web interface
- `POST /api/ocr` - Upload image and extract text
- `GET /api/health` - Check API status and available models

## Troubleshooting

If you see "Model not available" errors:
1. Visit `/api/health` to see available models
2. Set `GEMINI_MODEL` to one of the available models
3. Verify your API key is valid

Run `python test_gemini.py` to diagnose connection issues.
