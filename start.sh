#!/usr/bin/env sh
# Thin wrapper for local/monorepo use. Railway API service should use
# Root Directory=/backend and Config File=/backend/railway.toml (runs backend/start.sh).
set -eu
exec "$(dirname "$0")/backend/start.sh"
