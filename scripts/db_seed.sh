#!/usr/bin/env bash
# ============================================================
# KindBite — Seed the database with initial/demo data
# ============================================================
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"

echo "🌱 Seeding database..."

cd "$BACKEND"
source .venv/bin/activate

if [ -f "$ROOT/.env" ]; then
  export $(grep -v '^#' "$ROOT/.env" | grep -v '^$' | xargs)
fi

python3 -m app.scripts.seed_db

echo "✅ Database seeded."
