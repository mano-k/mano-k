#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [[ ! -d backend/.venv ]]; then
  python -m venv backend/.venv
fi

source backend/.venv/bin/activate
pip install -r backend/requirements.txt

set -a
if [[ -f .env ]]; then
  source .env
fi
set +a

cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
