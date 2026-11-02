#!/usr/bin/env bash
# ============================================================
# KindBite — DANGER: Reset database (dev only)
# ============================================================
set -e

echo ""
echo "⚠️  WARNING: This will DROP and recreate the database."
echo "   All data will be permanently deleted."
echo ""
read -p "Type 'RESET' to confirm: " confirm
if [ "$confirm" != "RESET" ]; then
  echo "Aborted."
  exit 1
fi

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"

cd "$BACKEND"
source .venv/bin/activate

if [ -f "$ROOT/.env" ]; then
  export $(grep -v '^#' "$ROOT/.env" | grep -v '^$' | xargs)
fi

echo "🗑️  Dropping database..."
alembic downgrade base

echo "🗄️  Re-running migrations..."
alembic upgrade head

echo "🌱 Seeding..."
python3 -m app.scripts.seed_db

echo "✅ Database reset and seeded."
