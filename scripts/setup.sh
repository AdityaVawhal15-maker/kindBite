#!/usr/bin/env bash
# ============================================================
# KindBite — Full project setup
# ============================================================
set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "============================================"
echo " KindBite — Project Setup"
echo "============================================"

# Check dependencies
command -v node >/dev/null 2>&1 || { echo "❌ Node.js not found. Please install Node.js 20+."; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "❌ Python 3 not found. Please install Python 3.11+."; exit 1; }
command -v git >/dev/null 2>&1 || { echo "❌ git not found."; exit 1; }

echo "✅ Node.js: $(node --version)"
echo "✅ npm: $(npm --version)"
echo "✅ Python: $(python3 --version)"

# Root npm install
echo ""
echo "📦 Installing root npm dependencies..."
cd "$ROOT" && npm install

# Frontend install
echo ""
echo "📦 Installing frontend npm dependencies..."
cd "$ROOT/frontend" && npm install

# Backend venv + deps
echo ""
echo "📦 Setting up Python virtual environment..."
cd "$ROOT/backend"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
touch .venv/.deps_installed
deactivate

# ML deps
echo ""
echo "📦 Installing ML dependencies..."
cd "$ROOT/ml"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q
touch .venv/.deps_installed
deactivate

# Create .env from example if not exists
if [ ! -f "$ROOT/.env" ]; then
  echo ""
  echo "📋 Creating .env from .env.example..."
  cp "$ROOT/.env.example" "$ROOT/.env"
  echo "⚠️  Please edit $ROOT/.env with your actual configuration!"
fi

echo ""
echo "============================================"
echo " ✅ Setup complete!"
echo ""
echo " Next steps:"
echo " 1. Edit .env with your PostgreSQL credentials"
echo " 2. Start PostgreSQL: docker compose up -d db"
echo " 3. Run migrations: npm run db:migrate"
echo " 4. Seed database: npm run db:seed"
echo " 5. Generate ML data: npm run ml:generate"
echo " 6. Train ML models: npm run ml:train"
echo " 7. Start app: npm run dev"
echo "============================================"
