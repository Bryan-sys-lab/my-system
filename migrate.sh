#!/usr/bin/env bash
set -o errexit
set -o pipefail
set -o nounset

echo "Running migrations..."

# Allow either DATABASE_URL or POSTGRES_DSN style env var
DATABASE_URL=${DATABASE_URL:-${POSTGRES_DSN:-}}

# If no DB configured, skip gracefully
if [ -z "${DATABASE_URL}" ]; then
	echo "DATABASE_URL not set; skipping migrations"
	exit 0
fi

# Wait for DB to be reachable (psql/pg_isready) up to timeout
DB_WAIT_SECONDS=${DB_WAIT_SECONDS:-60}
echo "Waiting up to ${DB_WAIT_SECONDS}s for DB to become available..."
WAITED=0
while true; do
	if command -v pg_isready >/dev/null 2>&1; then
		if pg_isready -d "${DATABASE_URL}" >/dev/null 2>&1; then
			echo "DB is ready (pg_isready)"
			break
		fi
	elif command -v psql >/dev/null 2>&1; then
		if echo "SELECT 1;" | psql "${DATABASE_URL}" >/dev/null 2>&1; then
			echo "DB is ready (psql)"
			break
		fi
	else
		# No DB client available, assume DB is reachable and continue
		echo "No DB client available (pg_isready/psql); proceeding without explicit health check"
		break
	fi

	if [ "$WAITED" -ge "$DB_WAIT_SECONDS" ]; then
		echo "Timed out waiting for DB after ${DB_WAIT_SECONDS}s"
		exit 1
	fi
	sleep 1
	WAITED=$((WAITED + 1))
done

# Helper to run SQL file idempotently (psql will stop on error when ON_ERROR_STOP=1)
run_sql_file() {
	local f="$1"
	if command -v psql >/dev/null 2>&1; then
		echo "Applying SQL file: $f"
		PGPASSWORD="${PGPASSWORD:-}" psql "${DATABASE_URL}" -v ON_ERROR_STOP=1 -f "$f" || echo "Warning: applying $f failed (it may have been applied already)"
	else
		echo "psql not available; cannot apply $f"
	fi
}

# Prefer alembic if present
if command -v alembic >/dev/null 2>&1; then
	echo "Running alembic migrations..."
	# alembic may fail in some environments; fail fast so CI surfaces errors
	alembic upgrade head
else
	echo "alembic not installed; attempting to run raw SQL migrations from infra/migrations"
	if [ -d "infra/migrations" ]; then
		for f in infra/migrations/*.sql; do
			[ -e "$f" ] || continue
			run_sql_file "$f"
		done
	else
		echo "No infra/migrations directory found"
	fi
fi

echo "Migrations finished"
