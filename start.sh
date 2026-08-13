#!/usr/bin/env bash
# Start script for Face Attendance API
set -e

PORT=46375
export PYTHONUNBUFFERED=1

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Create and activate virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt -q

echo "Starting Face Attendance API on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
