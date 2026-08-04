#!/usr/bin/env bash
# Railway start command for the Upvex FastAPI backend.
# Set Railway Root Directory to `backend` and Start Command to `./start.sh`.
set -euo pipefail

cd "$(dirname "$0")"

PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"

exec uvicorn app.main:app --host "$HOST" --port "$PORT"
