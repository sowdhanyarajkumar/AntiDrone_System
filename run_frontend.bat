@echo off
echo ========================================================
echo Starting Aeronex DRDO Anti-Drone Frontend
echo Problem Statement: SIH 26050
echo ========================================================
cd /d "%~dp0frontend"

npm run dev
pause
