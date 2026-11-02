#!/usr/bin/env bash
# ============================================================
# KindBite — Run Alembic database migrations
# ============================================================
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"

echo "🗄️  Running database migrations..."

cd "$BACKEND"
source .venv/bin/activate

if [ -f "$ROOT/.env" ]; then
  export $(grep -v '^#' "$ROOT/.env" | grep -v '^$' | xargs)
fi

alembic upgrade head

echo "✅ Migrations complete."
