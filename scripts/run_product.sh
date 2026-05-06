#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Stop old runs to avoid port conflicts
pkill -f "uvicorn app.main:app" >/dev/null 2>&1 || true
pkill -f "python voice/livekit_agent.py" >/dev/null 2>&1 || true
pkill -f "next dev -p 3000" >/dev/null 2>&1 || true

# Start backend (logs to .backend.log — check here if /v1/orchestrate fails)
(
  set -a
  source "$ROOT/backend/.env" 2>/dev/null || true
  source "$ROOT/voice/.env" 2>/dev/null || true
  set +a
  : >"$ROOT/.backend.log"
  nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend >>"$ROOT/.backend.log" 2>&1 &
  echo $! > "$ROOT/.backend.pid"
)

# Start voice worker
(
  set -a
  source "$ROOT/voice/.env" 2>/dev/null || true
  set +a
  export SSL_CERT_FILE="$(python -c 'import certifi; print(certifi.where())')"
  nohup python "$ROOT/voice/livekit_agent.py" dev >/dev/null 2>&1 &
  echo $! > "$ROOT/.voice.pid"
)

# Start frontend
nohup npm run dev --prefix frontend >/dev/null 2>&1 &
echo $! > "$ROOT/.frontend.pid"

sleep 2

echo "Product started"
echo "Frontend: http://127.0.0.1:3000"
echo "Backend:  http://127.0.0.1:8000"
echo "Backend log: $ROOT/.backend.log"
