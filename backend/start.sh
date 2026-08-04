#!/usr/bin/env bash
# Railway start command when Root Directory is set to `backend`.
# Prefer the repo-root start.sh + railway.toml for monorepo deploys.
set -euo pipefail

cd "$(dirname "$0")"

PORT="${PORT:-8000}"
HOST="${HOST:-0.0.0.0}"

exec uvicorn app.main:app --host "$HOST" --port "$PORT"
