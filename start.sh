#!/usr/bin/env bash
# Railway start command for the Upvex FastAPI backend (monorepo root).
set -euo pipefail

cd "$(dirname "$0")/backend"

PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"

# Fail early with a readable deploy log if required vars are missing.
# (backend/.env is gitignored and not present on Railway.)
if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "ERROR: DATABASE_URL is not set." >&2
  echo "Add it under Railway → Variables (Supabase session pooler URI," >&2
  echo "scheme postgresql+asyncpg://...). Without it the app defaults to" >&2
  echo "localhost Postgres, migrations crash, and /health stays unavailable." >&2
  exit 1
fi

echo "Starting uvicorn on ${HOST}:${PORT} (DATABASE_URL host: ${DATABASE_URL##*@})"

exec uvicorn app.main:app --host "$HOST" --port "$PORT"
