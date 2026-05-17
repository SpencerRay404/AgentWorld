#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# Activate Python venv
source .venv/bin/activate

# Start FastAPI backend in background
echo "Starting FastAPI backend on http://localhost:8000 ..."
uvicorn agent_world.api.server:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Start Vite frontend
echo "Starting Vite frontend on http://localhost:5173 ..."
cd gui
npm run dev &
FRONTEND_PID=$!

# Wait for either to exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
