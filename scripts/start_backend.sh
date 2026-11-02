#!/usr/bin/env bash
# ============================================================
# KindBite — Backend startup script
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR/.."
BACKEND="$ROOT/backend"

echo "🚀 Starting KindBite Backend..."

cd "$BACKEND"

if [ ! -d ".venv" ]; then
  echo "📦 Creating Python virtual environment..."
  PY_BIN=$(command -v python3.12 || echo "/opt/homebrew/bin/python3.12" || echo "python3")
  "$PY_BIN" -m venv .venv
fi

source .venv/bin/activate

# Install deps if needed
if [ ! -f ".venv/.deps_installed" ]; then
  echo "📦 Installing Python dependencies..."
  pip install --upgrade pip -q
  pip install -r requirements.txt -q
  touch .venv/.deps_installed
fi

# Copy .env if missing
if [ ! -f ".env" ] && [ -f "$ROOT/.env.example" ]; then
  echo "⚠️  No backend .env found. Copying from .env.example..."
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "   Please edit .env with your actual values."
fi

if [ -f "$ROOT/.env" ]; then
  export $(grep -v '^#' "$ROOT/.env" | grep -v '^$' | xargs)
fi

echo "🗄️  Starting FastAPI server on http://localhost:${BACKEND_PORT:-8000}"
uvicorn app.main:app --host "${BACKEND_HOST:-0.0.0.0}" --port "${BACKEND_PORT:-8000}" --reload
