#!/bin/bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "=================================================================="
echo " Starting Stock Price Prediction with LSTM & FinBERT Sentiment"
echo "=================================================================="

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    ./venv/bin/pip install -r backend/requirements.txt
fi

# Function to kill child processes on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "1. Launching FastAPI Backend on http://localhost:8000..."
PYTHONPATH=. ./venv/bin/python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "2. Launching React / Vite Frontend on http://localhost:5173..."
cd frontend
npm run dev -- --host &
FRONTEND_PID=$!
cd ..

echo ""
echo "=================================================================="
echo "  Application running!"
echo "  Frontend: http://localhost:5173"
echo "  Backend API: http://localhost:8000"
echo "  Interactive API Docs: http://localhost:8000/docs"
echo "=================================================================="
echo "Press Ctrl+C to terminate both servers."

wait
