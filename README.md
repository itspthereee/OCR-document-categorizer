# OCR Document Reader

A web app that extracts and categorizes text from document images using the Google Gemini API.

Upload an image, select the document language, and the app returns the extracted text organized into sections: header, items, amounts, and footer.

## Features

- Drag & drop or click to upload an image (PNG, JPG, JPEG, BMP, TIFF)
- Crop tool to select a specific area before running OCR
- Language selector (Thai, English, Chinese, Japanese, Korean, and more)
- Categorized output: header, items/products, amounts/totals, footer

## Stack

- **Frontend**: Vanilla JS + HTML/CSS, deployed on Vercel
- **Backend**: FastAPI + Python, deployed on Render
- **OCR**: Google Gemini 2.5 Flash API

## Local Development

1. Get a free API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

2. Set the environment variable:
   ```bash
   export GEMINI_API_KEY=your_key_here
   ```

3. Install dependencies and run:
   ```bash
   pip install -r requirements.txt
   uvicorn web_app:app --reload
   ```

4. Open http://localhost:8000

## Deployment

### Backend (Render)

1. Create a new **Web Service** on [Render](https://render.com)
2. Connect your GitHub repo, set branch to `main`
3. Use these settings:
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `uvicorn web_app:app --host 0.0.0.0 --port $PORT`
4. Add `GEMINI_API_KEY` in the Environment tab

### Frontend (Vercel)

1. Import the repo on [Vercel](https://vercel.com)
2. Set the **Root Directory** to `web`
3. Update the `api-base` meta tag in `web/index.html` to point to your Render URL:
   ```html
   <meta name="api-base" content="https://your-service.onrender.com" />
   ```

## Free Tier Limits

| Resource | Limit |
|---|---|
| Gemini 2.5 Flash requests | 20 / day |
| Render free tier | Spins down after inactivity — first request takes ~30s |
