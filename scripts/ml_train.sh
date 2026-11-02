#!/usr/bin/env bash
# ============================================================
# KindBite — Train all ML models
# ============================================================
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ML="$ROOT/ml"

echo "🤖 Training KindBite ML models..."
echo "   This may take several minutes."
echo ""

cd "$ML"
source .venv/bin/activate

if [ -f "$ROOT/.env" ]; then
  export $(grep -v '^#' "$ROOT/.env" | grep -v '^$' | xargs)
fi

echo "1/4 Preprocessing data..."
python3 scripts/preprocess_data.py

echo "2/4 Training demand forecasting model..."
python3 scripts/train_demand_model.py

echo "3/4 Training surplus prediction model..."
python3 scripts/train_surplus_model.py

echo "4/4 Training waste risk classifier..."
python3 scripts/train_risk_model.py

echo ""
echo "📈 Evaluating all models..."
python3 scripts/evaluate_models.py

echo ""
echo "✅ All models trained and saved to ml/models/artifacts/"
