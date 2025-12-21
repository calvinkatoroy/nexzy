# Run Automated Tests for Nexzy
# Backend (pytest) + Frontend (vitest)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Nexzy Automated Test Suite" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Backend Tests
Write-Host "[1/2] Running Backend Tests (pytest)..." -ForegroundColor Yellow
Write-Host ""

cd nexzy-backend

# Install test dependencies if needed
if (-not (Test-Path "venv\Scripts\pytest.exe")) {
    Write-Host "Installing pytest..." -ForegroundColor Green
    .\venv\Scripts\pip install pytest pytest-asyncio httpx
}

# Run pytest
Write-Host "Executing pytest..." -ForegroundColor Green
.\venv\Scripts\pytest tests\ -v --tb=short

$backendExitCode = $LASTEXITCODE

cd ..

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Frontend Tests
Write-Host "[2/2] Running Frontend Tests (vitest)..." -ForegroundColor Yellow
Write-Host ""

cd nexzy-frontend

# Install test dependencies if needed
if (-not (Test-Path "node_modules\vitest")) {
    Write-Host "Installing vitest and testing libraries..." -ForegroundColor Green
    npm install -D vitest @vitejs/plugin-react jsdom @testing-library/react @testing-library/jest-dom
}

# Run vitest
Write-Host "Executing vitest..." -ForegroundColor Green
npm run test

$frontendExitCode = $LASTEXITCODE

cd ..

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Test Summary" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

if ($backendExitCode -eq 0) {
    Write-Host "✅ Backend Tests: PASSED" -ForegroundColor Green
} else {
    Write-Host "❌ Backend Tests: FAILED" -ForegroundColor Red
}

if ($frontendExitCode -eq 0) {
    Write-Host "✅ Frontend Tests: PASSED" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend Tests: FAILED" -ForegroundColor Red
}

Write-Host ""
Write-Host "Test reports available in:" -ForegroundColor Cyan
Write-Host "  - Backend: nexzy-backend/.pytest_cache/" -ForegroundColor Gray
Write-Host "  - Frontend: nexzy-frontend/coverage/" -ForegroundColor Gray
Write-Host ""

# ===================== Penjelasan Detail =====================
Write-Host "Test Details:" -ForegroundColor Cyan
Write-Host "- Backend (pytest):" -ForegroundColor Yellow
Write-Host "  • Menguji integrasi AI, endpoint API (root, health, stats, scan, alerts, websocket), autentikasi, validasi input, dan error handling." -ForegroundColor Gray
Write-Host "  • PASS artinya semua endpoint merespons benar, validasi & autentikasi berjalan, serta tidak ada error kritis." -ForegroundColor Gray
Write-Host "- Frontend (vitest):" -ForegroundColor Yellow
Write-Host "  • Menguji komponen UI utama (StatsCard, Navigation), rendering, interaksi, dan tampilan data." -ForegroundColor Gray
Write-Host "  • PASS artinya komponen berhasil dirender, interaksi & data tampil sesuai harapan." -ForegroundColor Gray
Write-Host "=============================================================" -ForegroundColor Cyan

if ($backendExitCode -ne 0 -or $frontendExitCode -ne 0) {
    exit 1
}

exit 0
