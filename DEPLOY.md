# Deployment Guide

## Fixed Issues
✅ Removed EasyOCR dependency (now using Gemini only)
✅ Added automatic model detection and fallback
✅ Added `/api/health` endpoint to check API status
✅ Improved error messages with available models list
✅ Updated google-generativeai to latest version

## Deploy to Koyeb

1. **Set Environment Variable**
   - Go to your Koyeb service settings
   - Add environment variable: `GEMINI_API_KEY` with your API key
   - (Optional) Add `GEMINI_MODEL` to specify a model (e.g., `gemini-1.5-flash`)

2. **Redeploy**
   - Push changes to GitHub
   - Trigger redeploy on Koyeb
   - Or use Koyeb's manual redeploy button

3. **Verify Deployment**
   - Visit: `https://your-app.koyeb.app/api/health`
   - Check that `status: "ok"` and models are listed
   - If models list is empty, your API key may be invalid

## Test Locally

```bash
# Set API key
$env:GEMINI_API_KEY = "your-api-key-here"

# Install dependencies
pip install -r requirements.txt

# Run server
python web_app.py
```

Then open http://localhost:8000

## Troubleshooting

### "Model not available" error
- Check `/api/health` endpoint to see available models
- Set `GEMINI_MODEL` environment variable to one of the available models
- Verify your API key has access to Gemini models

### API key not working
- Make sure you're using a valid Google AI Studio API key
- Create one at: https://makersuite.google.com/app/apikey
- The key should start with "AI..."

### Connection issues
- Check CORS settings if deploying frontend separately
- Verify the frontend's api-base meta tag points to correct backend URL
