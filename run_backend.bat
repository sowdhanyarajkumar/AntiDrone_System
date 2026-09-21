@echo off
echo ========================================================
echo Starting Aeronex DRDO Anti-Drone Backend Server
echo Problem Statement: SIH 26050
echo ========================================================
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found! Please ensure Python 3.10 is installed and .venv is created.
    pause
    exit /b 1
)

echo Activating Python Virtual Environment...
set PYTHONPATH=%~dp0backend
.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload --app-dir backend
pause
