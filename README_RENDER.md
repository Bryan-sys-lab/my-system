## 7. Automation & Operations

- **Backups:**
  - Run `bash scripts/backup.sh` to back up Postgres and Minio data to `/data/backups/`.
  - On failure, alerts are sent to Slack, webhook, or WhatsApp if configured.
- **Log Shipping:**
  - Logs in `/data/app.log` are tailed and can be shipped to an external endpoint by setting the `LOG_ENDPOINT` env var.
- **Health Checks:**
  - Health checks run before every deploy. Failures trigger alerts.
- **Environment Sync:**
  - All required env vars are checked before deploy. Missing vars block deploy and trigger alerts.
- **Alerting:**
  - Alerts are sent via webhook, Slack, or WhatsApp (Twilio) if the relevant env vars are set.
# Render Deployment Guide (Test Mode)

## 1. Repo Setup
- Create a **new GitHub repo**.
- Upload the full contents of this folder to it.

## 2. Render Blueprint Deploy
1. Log in to [Render](https://render.com/).
2. Click **New → Blueprint**.
3. Connect your GitHub repo.

4. Render will read the new `render.yaml` (now included in this repo) and create:
   - **Web Service** (FastAPI API)
   - **Scheduler Worker** (low-frequency collectors)
   - **Celery Worker** (background jobs)
   - **Postgres** (Free tier)
   - **Redis** (Free tier)
5. All required environment variables and service connections are now defined in `render.yaml` for automatic setup.

## 3. Environment Variables
Set the following for all services:
```
TEST_MODE=true
WATCHER_TICK_SECONDS=3600
CELERY_CONCURRENCY=1
REDIS_URL=redis://<your-render-redis-url>
DATABASE_URL=postgres://<your-render-db-url>
```

## 4. Test Mode Behavior
- Watchers tick every **hour** instead of every minute.
- Celery runs **1 worker process**.
- ML pipeline runs **in passive logging mode** only.
- No aggressive scraping or deep crawling.

## 5. Triggering Collectors Manually
Once deployed, you can trigger any collector manually:
```
curl -X POST https://<your-domain>/run_collector   -H "Content-Type: application/json"   -d '{"name":"scrape_and_store","url":"https://example.com"}'
```

## 6. Going Live
When ready for production:
```
TEST_MODE=false
WATCHER_TICK_SECONDS=60
CELERY_CONCURRENCY=4
```
- Upgrade Redis and Postgres to Standard or higher.
- Scale workers up.
