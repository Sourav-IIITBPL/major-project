#!/usr/bin/env bash
# =============================================================================
# deploy.sh — Production & Local Deployment Script for ML Cryptographic Engine
# =============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "===================================================================="
echo "  ML-Assisted Adaptive Cryptographic Engine — Deployment"
echo "===================================================================="

# Check Python environment
if [ -d "$VENV_DIR" ]; then
    PYTHON="$VENV_DIR/bin/python"
    UVICORN="$VENV_DIR/bin/uvicorn"
else
    PYTHON="python3"
    UVICORN="uvicorn"
fi

# 1. Docker Deployment Mode
if [ "$1" = "--docker" ]; then
    echo "🐳 Launching via Docker Compose..."
    docker compose up -d --build
    echo "✔ Deployment complete! Access the platform at http://localhost:8000"
    docker compose ps
    exit 0
fi

# 2. Dual Development Mode (Backend 8000 + Frontend 3000)
if [ "$1" = "--dev" ]; then
    echo "💻 Starting Development Mode (Backend :8000 + Frontend Vite :3000)..."
    trap 'kill $(jobs -p) 2>/dev/null || true' EXIT

    echo "▶ Starting FastAPI Backend on http://$HOST:$PORT..."
    $UVICORN backend.api:app --reload --host "$HOST" --port "$PORT" &
    BACKEND_PID=$!

    echo "▶ Starting Vite Frontend on http://localhost:3000..."
    cd frontend
    npm run dev -- --host &
    FRONTEND_PID=$!
    cd ..

    echo ""
    echo "===================================================================="
    echo "  ✔ Development Servers Running:"
    echo "    - Frontend Dashboard: http://localhost:3000"
    echo "    - Backend REST API:   http://localhost:$PORT"
    echo "    - Swagger API Docs:   http://localhost:$PORT/docs"
    echo "===================================================================="
    echo "Press Ctrl+C to terminate both servers."
    wait
    exit 0
fi

# 3. Unified Production Deployment (Single Port)
echo "📦 Checking Frontend Production Build (dist/)..."
if [ ! -d "frontend/dist" ] || [ "$1" = "--build" ]; then
    echo "⚙ Compiling React Frontend Assets via Vite..."
    cd frontend
    npm run build
    cd ..
    echo "✔ Frontend built successfully."
fi

echo ""
echo "🚀 Starting Unified Production Server on http://$HOST:$PORT..."
echo "   - React 19 Frontend: http://$HOST:$PORT/"
echo "   - REST API Endpoints: http://$HOST:$PORT/api/..."
echo "   - Interactive Swagger Docs: http://$HOST:$PORT/docs"
echo "===================================================================="

exec $UVICORN backend.api:app --host "$HOST" --port "$PORT" --workers 2
