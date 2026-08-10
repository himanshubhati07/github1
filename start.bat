@echo off
REM Start script for Face Attendance API (Windows)
set PORT=53677
set PYTHONUNBUFFERED=1

cd /d "%~dp0"

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt -q

echo Starting Face Attendance API on port %PORT%...
uvicorn app.main:app --host 0.0.0.0 --port 53677 --reload
