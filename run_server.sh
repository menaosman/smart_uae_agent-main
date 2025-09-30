#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

if [ ! -x "$ROOT/.venv/bin/python" ]; then
  echo "Creating virtualenv..."
  python3 -m venv "$ROOT/.venv"
fi
source "$ROOT/.venv/bin/activate"

if [ -f "$ROOT/.env" ]; then
  set -a; source "$ROOT/.env"; set +a
fi

: "${SMARTUAE_LLM:=openai}"
: "${SMARTUAE_KB:=uae_knowledge_expanded.json}"
: "${USE_ALADHAN_API:=false}"

python -m pip install -r "$ROOT/requirements.txt" >/dev/null

echo "SMARTUAE_LLM=$SMARTUAE_LLM"
echo "SMARTUAE_KB=$SMARTUAE_KB"
echo "USE_ALADHAN_API=$USE_ALADHAN_API"

exec python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
