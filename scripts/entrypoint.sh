#!/bin/bash
set -e

# 1. Database Migration Automation
if [ -d "/app/infra/migrations" ]; then
  echo "Running DB migrations..."
  for f in /app/infra/migrations/*.sql; do
    echo "Applying $f..."
    PGPASSWORD="$POSTGRES_PASSWORD" psql "$DATABASE_URL" -f "$f" || true
  done
fi

# 2. Dependency Management (pip-compile)
if [ -f "/app/requirements.in" ]; then
  echo "Compiling requirements.in..."
  pip install pip-tools
  pip-compile /app/requirements.in
fi

# 8. Data Directory Initialization
mkdir -p /data/faiss
if [ ! -f /data/faiss/images_meta.json ]; then
  echo "[]" > /data/faiss/images_meta.json
fi

exec "$@"
