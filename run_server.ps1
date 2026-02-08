# Set environment variables
$env:GEMINI_API_KEY = "AIzaSyBagWZAixbmkgVvs84Wx_IbPGD1GNJdJmA"
$env:PORT = "8000"

# Run the server
Write-Host "🚀 Starting OCR Document Reader..."
Write-Host "📍 Server will be available at: http://localhost:8000"
Write-Host "❌ Press CTRL+C to stop the server`n"

.\.venv\Scripts\python.exe web_app.py
