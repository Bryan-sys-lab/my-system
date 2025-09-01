#!/usr/bin/env bash
set -euo pipefail

# Simple developer start script for local runs
# Usage: ./scripts/dev_start.sh [--no-docker]

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

NO_DOCKER=0
if [[ "${1:-}" == "--no-docker" ]]; then
  NO_DOCKER=1
fi

echo "[dev_start] root: $ROOT"

# 1) Create virtualenv if missing
if [ ! -d ".venv" ]; then
  echo "[dev_start] creating venv .venv"
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install -U pip

# Set test/dev shim to avoid installing heavy native ML packages during local dev
export SKIP_HEAVY_DEPS=1
echo "[dev_start] installing python requirements (heavy deps skipped via SKIP_HEAVY_DEPS=1)"
pip install -r requirements.txt || true

# 2) Optionally start docker-compose services (Postgres/Redis/MinIO)
if [ "$NO_DOCKER" -eq 0 ] && command -v docker-compose >/dev/null 2>&1; then
  echo "[dev_start] bringing up docker-compose (postgres/redis/minio)"
  docker-compose up -d
else
  echo "[dev_start] skipping docker-compose (either --no-docker passed or docker-compose not found)"
fi

# 3) Export convenient envs for local run
export PYTHONPATH="$ROOT"
export SKIP_HEAVY_DEPS=${SKIP_HEAVY_DEPS:-1}

# 4) Run migrations
if [ -x "./migrate.sh" ]; then
  echo "[dev_start] running migrations"
  ./migrate.sh
else
  echo "[dev_start] migrate.sh not found or not executable; skipping migrations"
fi

# 5) Ensure logs directory
mkdir -p ./logs

# 6) Start uvicorn in background
UVICORN_LOG=./logs/uvicorn.log
if pgrep -f "uvicorn apps.api.main" >/dev/null 2>&1; then
  echo "[dev_start] uvicorn already running"
else
  echo "[dev_start] starting uvicorn -> $UVICORN_LOG"
  nohup .venv/bin/python -m uvicorn apps.api.main:app --host 0.0.0.0 --port 10000 --log-level info > "$UVICORN_LOG" 2>&1 &
  sleep 0.5
  echo "[dev_start] uvicorn started (pid=$(pgrep -f "uvicorn apps.api.main" | head -n1))"
fi

echo "[dev_start] done. Logs: $UVICORN_LOG"
echo "To start a worker in another terminal:"
echo "  source .venv/bin/activate && celery -A apps.workers.tasks worker --loglevel=info"

exit 0
