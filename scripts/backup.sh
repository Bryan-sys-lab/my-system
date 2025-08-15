#!/bin/bash
# 4. Backup Automation
set -e
BACKUP_DIR="/data/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Postgres backup
if [ -n "$DATABASE_URL" ]; then
  echo "Backing up Postgres..."
  PGPASSWORD="$POSTGRES_PASSWORD" pg_dump "$DATABASE_URL" > "$BACKUP_DIR/db.sql"
fi

# Minio backup (requires mc CLI)
if command -v mc >/dev/null 2>&1; then
  echo "Backing up Minio..."
  mc alias set minio http://$MINIO_ENDPOINT $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD
  mc cp --recursive minio/$MINIO_BUCKET "$BACKUP_DIR/minio/"
fi

if [ $? -eq 0 ]; then
  echo "Backup complete: $BACKUP_DIR"
else
  python3 /app/scripts/alert.py "Backup failed for $BACKUP_DIR!"
fi
