#!/usr/bin/env sh
# Railway start command when Root Directory is set to `backend`.
# Prefer the repo-root start.sh + railway.toml for monorepo deploys.
set -eu

cd "$(dirname "$0")"

PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"

if [ -x /app/.venv/bin/python ]; then
  PYTHON=/app/.venv/bin/python
elif [ -n "${VIRTUAL_ENV:-}" ] && [ -x "${VIRTUAL_ENV}/bin/python" ]; then
  PYTHON="${VIRTUAL_ENV}/bin/python"
else
  PYTHON=python
fi

echo "=== Upvex start (backend) ==="
echo "cwd=$(pwd) host=${HOST} port=${PORT} python=${PYTHON}"
echo "DATABASE_URL set: $([ -n "${DATABASE_URL:-}" ] && echo yes || echo NO)"

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL is not set in the process environment." >&2
  exit 1
fi

exec "$PYTHON" -m uvicorn app.main:app --host "$HOST" --port "$PORT"
