# Deployment & Readiness Checklist

This document lists the minimal steps, env vars, and readiness checks to deploy the `b-search` service (Render, Docker, or similar).

## Required services
- PostgreSQL (version >= 12)
- Redis
- MinIO (optional but required for object storage features)

## Required environment variables
Set these before starting the service (example names used in repo):

- DATABASE_URL (or POSTGRES_DSN): postgresql+psycopg://user:pass@host:5432/dbname
- REDIS_URL: redis://host:6379/0
- MINIO_ROOT_USER & MINIO_ROOT_PASSWORD
- MINIO_ENDPOINT (e.g., http://minio:9000)
- SENTRY_DSN (optional)
- ETH_RPC_URL, ETHERSCAN_API_KEY (if using crypto features)
- BLOCKSTREAM_API_BASE (optional)

## Optional but recommended
- TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN for alerts
- GOOGLE_GEOLOCATION_API_KEY for geo features

## Startup order
1. Provision and start PostgreSQL, Redis, and MinIO (if used).
2. Run migrations:

```bash
# from repository root
./migrate.sh
```

3. Validate environment (optional but recommended):

```bash
python3 scripts/validate_env.py
```

4. Start services (API / workers) using your preferred method (systemd, docker-compose, Render service):

- For Docker Compose, use the repository `docker/` configs or the provided `render.yaml`.

## Health and readiness checks
- API health endpoint: `GET /healthz` should return 200 and `{"status":"ok"}`
- Metrics endpoint: `GET /metrics` should return Prometheus text and include `api_requests_total`
- DB connectivity: `psql "$DATABASE_URL" -c 'SELECT 1;'`
- Redis connectivity: `redis-cli -u "$REDIS_URL" ping`

## Render notes
- Ensure `DATABASE_URL`, `REDIS_URL`, and `MINIO_*` variables are set in Render's dashboard for the service.
- Add a prestart command to run migrations and environment validation:

```
./migrate.sh && python3 scripts/validate_env.py
```

## Rollback and migrations
- Migrations should be idempotent where possible. If using Alembic, always run `alembic upgrade head`.
- Ensure backups of DB before major schema changes.

## Troubleshooting
- If API fails to start, check logs for missing environment variables, DB connection errors, or missing system packages (tesseract, ffmpeg).

