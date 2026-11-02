#!/usr/bin/env bash
# ============================================================
# KindBite — Run backend tests
# ============================================================
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"

echo "🧪 Running backend tests..."

cd "$BACKEND"
source .venv/bin/activate

if [ -f "$ROOT/.env" ]; then
  export $(grep -v '^#' "$ROOT/.env" | grep -v '^$' | xargs)
fi
export PYTHONPATH="$BACKEND:$PYTHONPATH"
pytest tests/ -v --tb=short

echo "✅ Backend tests complete."
