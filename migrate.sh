#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

echo "Running migrations..."

# Wait for DATABASE_URL to be set or for a reachable DB
if [ -z "${DATABASE_URL:-}" ]; then
	echo "DATABASE_URL not set; skipping migrations"
	exit 0
fi

# Try alembic upgrade if available
if command -v alembic >/dev/null 2>&1; then
	echo "Running alembic migrations..."
	alembic upgrade head || echo "alembic upgrade failed or no migrations configured"
else
	echo "alembic not installed; attempting to run raw SQL migrations from infra/migrations"
	if [ -d "infra/migrations" ]; then
		if command -v psql >/dev/null 2>&1; then
			for f in infra/migrations/*.sql; do
				[ -e "$f" ] || continue
				echo "Applying $f"
				psql "$DATABASE_URL" -f "$f" || echo "Failed to apply $f"
			done
		else
			echo "psql not available in container; skipping raw SQL migrations"
		fi
	else
		echo "No infra/migrations directory found"
	fi
fi

echo "Migrations finished"
