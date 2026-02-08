# Set environment variables
# IMPORTANT: Set GEMINI_API_KEY in your shell before running this script.
$env:PORT = "8000"

if (-not $env:GEMINI_API_KEY) {
	Write-Host "❌ GEMINI_API_KEY is not set."
	Write-Host "   PowerShell: $env:GEMINI_API_KEY = \"your-key\""
	exit 1
}

# Run the server
Write-Host "🚀 Starting OCR Document Reader..."
Write-Host "📍 Server will be available at: http://localhost:8000"
Write-Host "❌ Press CTRL+C to stop the server`n"

.\.venv\Scripts\python.exe web_app.py
