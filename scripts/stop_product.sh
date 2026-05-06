#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

for f in .backend.pid .voice.pid .frontend.pid; do
  if [[ -f "$f" ]]; then
    kill "$(cat "$f")" >/dev/null 2>&1 || true
    rm -f "$f"
  fi
done

pkill -f "uvicorn app.main:app" >/dev/null 2>&1 || true
pkill -f "python .*/voice/livekit_agent.py" >/dev/null 2>&1 || true
pkill -f "next dev -p 3000" >/dev/null 2>&1 || true

echo "Product stopped"
