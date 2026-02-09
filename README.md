# OCR-document-categorizer

Simple OCR web app using EasyOCR with a drag-and-drop frontend.

## Local setup

Install dependencies:

    pip install -r requirements.txt

Run the server:

    python web_app.py

Open http://localhost:8000.

## Render deployment

Create a new Web Service and use:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn web_app:app --host 0.0.0.0 --port $PORT`

The service serves the frontend from `/` and the OCR API at `/api/ocr`.

## Koyeb deployment

Koyeb sometimes fails to detect Python buildpacks, so this repo includes a
Dockerfile. Configure the service to build from Dockerfile:

- Build: Dockerfile
- Start command: use the Dockerfile default

The app listens on `$PORT` (defaults to 8000).

### OCR languages

The UI includes a language selector. The backend also accepts an optional
`languages` form field with comma-separated EasyOCR language codes, for example
`en` or `th,en`.

### CORS for Vercel

Set `ALLOWED_ORIGINS` on Render to your Vercel domain, for example:

    https://your-frontend.vercel.app

You can also use `*` for testing.

### Frontend API base

If you deploy the frontend separately, edit the meta tag in
[web/index.html](web/index.html) to set the backend URL:

    <meta name="api-base" content="https://your-backend.onrender.com" />
