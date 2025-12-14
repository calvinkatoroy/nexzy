# Nexzy - Start All Services
# This script starts the AI Service, Backend, and Frontend

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  NEXZY - START ALL SERVICES" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Store the root directory
$ROOT_DIR = $PSScriptRoot

# Function to start a service in a new window
function Start-Service {
    param(
        [string]$Name,
        [string]$Path,
        [string]$Command,
        [string]$Color
    )
    
    Write-Host "Starting $Name..." -ForegroundColor $Color
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$Path'; $Command"
}

Write-Host "Starting services in separate windows..." -ForegroundColor Yellow
Write-Host ""

# Start AI Service (Port 8000)
Start-Service -Name "AI Service" `
              -Path "$ROOT_DIR\ai-service" `
              -Command ".\start.ps1" `
              -Color "Magenta"
Write-Host "  ✅ AI Service starting on port 8000" -ForegroundColor Green

Start-Sleep -Seconds 2

# Start Backend (Port 8001)
Start-Service -Name "Backend API" `
              -Path "$ROOT_DIR\nexzy-backend" `
              -Command ".\start.ps1" `
              -Color "Blue"
Write-Host "  ✅ Backend API starting on port 8001" -ForegroundColor Green

Start-Sleep -Seconds 2

# Start Frontend (Port 5173)
Start-Service -Name "Frontend" `
              -Path "$ROOT_DIR\nexzy-frontend" `
              -Command "npm run dev" `
              -Color "Cyan"
Write-Host "  ✅ Frontend starting on port 5173" -ForegroundColor Green

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  ALL SERVICES STARTING!" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services:" -ForegroundColor White
Write-Host "  AI Service:  http://localhost:8000" -ForegroundColor Magenta
Write-Host "  Backend API: http://localhost:8001" -ForegroundColor Blue
Write-Host "  Frontend:    http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
Write-Host "API Documentation:" -ForegroundColor White
Write-Host "  Backend:     http://localhost:8001/docs" -ForegroundColor Blue
Write-Host "  AI Service:  http://localhost:8000/docs" -ForegroundColor Magenta
Write-Host ""
Write-Host "Health Checks:" -ForegroundColor White
Write-Host "  Backend:     http://localhost:8001/health" -ForegroundColor Blue
Write-Host "  AI Service:  http://localhost:8000/health" -ForegroundColor Magenta
Write-Host ""
Write-Host "Each service is running in its own window." -ForegroundColor Yellow
Write-Host "Close each window or press Ctrl+C to stop services." -ForegroundColor Yellow
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
