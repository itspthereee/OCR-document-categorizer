# OCR-document-categorizer

Web app that extracts and categorizes text from document images using Google Gemini Flash.

## Local setup

Run the server:

    python web_app.py

Open http://localhost:8000.

Set `GEMINI_API_KEY` environment variable before running.

## Render deployment

Create a new Web Service and use:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn web_app:app --host 0.0.0.0 --port $PORT`

Set `GEMINI_API_KEY` in the Environment tab.

## Frontend API base

If you deploy the frontend separately (e.g. Vercel), edit the meta tag in
[web/index.html](web/index.html) to set the backend URL:

    <meta name="api-base" content="https://your-backend.onrender.com" />
