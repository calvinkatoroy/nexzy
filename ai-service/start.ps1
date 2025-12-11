# AI Service Startup Script
Write-Host "Starting Nexzy AI Scoring Service..." -ForegroundColor Cyan

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "WARNING: .env file not found! Creating from example..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "Created .env file. Please add your GEMINI_API_KEY!" -ForegroundColor Yellow
        Write-Host "" 
        Write-Host "Get your API key from:" -ForegroundColor White
        Write-Host "  -> https://aistudio.google.com/app/apikey" -ForegroundColor Cyan
        Write-Host ""
        Read-Host "Press Enter after you've added your API key to .env"
    }
}

# Load .env
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
        }
    }
}

# Check for API key
$apiKey = [System.Environment]::GetEnvironmentVariable("GEMINI_API_KEY")
if (-not $apiKey -or $apiKey -eq "your_gemini_api_key_here" -or $apiKey -eq "") {
    Write-Host "ERROR: GEMINI_API_KEY not configured!" -ForegroundColor Red
    Write-Host "   Service will run in MOCK mode (returns fake data)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To enable real AI analysis:" -ForegroundColor White
    Write-Host "  1. Get API key from: https://aistudio.google.com/app/apikey" -ForegroundColor Cyan
    Write-Host "  2. Add to .env: GEMINI_API_KEY=your_key_here" -ForegroundColor Cyan
    Write-Host "  3. Restart this service" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "Starting AI Service on port 8001..." -ForegroundColor Green
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
