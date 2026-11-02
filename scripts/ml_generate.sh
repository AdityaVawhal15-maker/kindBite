#!/usr/bin/env bash
# ============================================================
# KindBite — Generate synthetic ML training dataset
# ============================================================
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ML="$ROOT/ml"

echo "📊 Generating synthetic dataset..."
cd "$ML"
source .venv/bin/activate

if [ -f "$ROOT/.env" ]; then
  export $(grep -v '^#' "$ROOT/.env" | grep -v '^$' | xargs)
fi

python3 scripts/generate_dataset.py

echo "✅ Dataset generated in $ROOT/data/synthetic/"
