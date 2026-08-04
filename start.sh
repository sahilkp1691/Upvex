#!/usr/bin/env bash
# Railway start command for the Upvex FastAPI backend (monorepo root).
set -euo pipefail

cd "$(dirname "$0")/backend"

PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"

exec uvicorn app.main:app --host "$HOST" --port "$PORT"
