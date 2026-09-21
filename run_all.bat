@echo off
echo ========================================================
echo Launching Aeronex Anti-Drone System (Backend + Frontend)
echo SIH Problem Statement ID: 26050 (DRDO)
echo ========================================================
cd /d "%~dp0"

start "Aeronex Backend (FastAPI)" cmd /c "run_backend.bat"
timeout /t 2 /nobreak >nul
start "Aeronex Frontend (Vite/React)" cmd /c "run_frontend.bat"

echo.
echo Both systems initiated:
echo - Backend API: http://localhost:8000
echo - Swagger Docs: http://localhost:8000/docs
echo - Frontend UI: http://localhost:5173
echo.
pause
