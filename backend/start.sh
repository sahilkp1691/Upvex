#!/usr/bin/env sh
# Canonical Railway start for the API when Root Directory = /backend.
set -eu

cd "$(dirname "$0")"

PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"

# Prefer Railpack's venv; fall back to PATH.
if [ -x /app/.venv/bin/python ]; then
  PYTHON=/app/.venv/bin/python
elif [ -n "${VIRTUAL_ENV:-}" ] && [ -x "${VIRTUAL_ENV}/bin/python" ]; then
  PYTHON="${VIRTUAL_ENV}/bin/python"
else
  PYTHON=python
fi

echo "=== Upvex API start ==="
echo "cwd=$(pwd) host=${HOST} port=${PORT} python=${PYTHON}"
echo "DATABASE_URL set: $([ -n "${DATABASE_URL:-}" ] && echo yes || echo NO)"
if [ -n "${DATABASE_URL:-}" ]; then
  # Print host only (after @), never the password.
  echo "DATABASE_URL host: ${DATABASE_URL##*@}"
fi
echo "APP_ENV=${APP_ENV:-} RAILWAY_ENVIRONMENT=${RAILWAY_ENVIRONMENT:-}"
# `|| true` so an empty grep match cannot abort under set -e.
echo "keys: $(env | cut -d= -f1 | grep -E '^(DATABASE|SUPABASE|APP_|CORS|CELERY|REDIS|PORT|RAILWAY)' | sort | tr '\n' ' ' || true)"

if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL is not set in the process environment." >&2
  echo "Railway → API service → Variables → add DATABASE_URL" >&2
  echo "Use Supabase Session pooler (…pooler.supabase.com:5432), not db.<ref>.supabase.co." >&2
  exit 1
fi

case "${DATABASE_URL}" in
  *pooler.supabase.com*) ;;
  *supabase.co*)
    echo "WARNING: DATABASE_URL looks like Supabase direct (IPv6). Prefer …pooler.supabase.com" >&2
    ;;
esac

exec "$PYTHON" -m uvicorn app.main:app --host "$HOST" --port "$PORT"
