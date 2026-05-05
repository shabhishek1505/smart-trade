@echo off
echo.
echo ========================================
echo Smart-Trade Local Startup
echo ========================================
echo.
echo Starting services in separate windows...
echo Press any key to continue or Ctrl+C to cancel
echo.
pause

echo.
echo 1. Starting API Server (Port 8000)...
start cmd /k "cd /d D:\Code\smart-trade && python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3

echo 2. Starting Frontend (Port 3000)...
start cmd /k "cd /d D:\Code\smart-trade\frontend && npm start"

timeout /t 3

echo 3. Starting Worker Service...
start cmd /k "cd /d D:\Code\smart-trade && python worker_service.py"

echo.
echo ========================================
echo Services starting...
echo API:      http://localhost:8000
echo Docs:     http://localhost:8000/docs
echo Frontend: http://localhost:3000
echo ========================================
echo.
