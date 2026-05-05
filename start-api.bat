@echo off
cd /d D:\Code\smart-trade
echo Starting Smart-Trade API Server on http://localhost:8000
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
pause
