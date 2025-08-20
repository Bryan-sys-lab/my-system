# b-search (Consolidated Modular System)

A production-grade, modular OSINT + data collection and enrichment 

- **Collectors**: headless browser (Selenium), RSS, site-specific, social (generic), files, images & video.
- **Live Search Pipelines**: FastAPI + Celery workers with Redis broker for async scraping & enrichment.
- **Enrichment**: OCR (Tesseract via `pytesseract`), ASR (OpenAI Whisper local), NER (spaCy), entity/link resolution, deduplication, similarity.
- **Crypto Tracking**: BTC (Blockstream) + ETH (Etherscan/JSON-RPC) connectors, wallet clustering heuristics, spike alerts.
- **Storage**: PostgreSQL (SQLAlchemy), MinIO object storage, optional Elasticsearch.
- **Monitoring**: Prometheus metrics & Grafana dashboards, structured logging, health checks, Sentry-ready.
- **Alerting**: WhatsApp (Twilio), Email (SMTP).
- **Labeling**: Label Studio service plugged into `docker-compose` for analyst feedback loops.
- **BI Access**: Read-only Postgres role for analysts to connect from external BI tools to *current research projects only*.
- **Security**: Minimal privileges, API keys in env, input validation, rate limiting, sandboxing where applicable.

---

## Quick Start

```bash
# 1) Provision env
cp .env.example .env

# 2) Build & run
docker compose up -d --build

# 3) Visit services
# API Gateway: http://localhost:8080/docs
# Label Studio: http://localhost:8081
# MinIO Console: http://localhost:9001 (user: minioadmin / pass: minioadmin)
# Grafana: http://localhost:3000 (admin / admin)
```

> **Note**: Some collectors need API keys (Etherscan/Twilio/Sentry). Without keys, those modules gracefully no-op and log actionable errors (not stubs, just disabled via config).

## Layout

```
apps/
  api/
  workers/
  ui/             # (optional future frontend)
services/
  postgres/
  redis/
  minio/
  label-studio/
  grafana-prom/
libs/
  collectors/
  enrichment/
  crypto/
  storage/
  common/
infra/
  docker/
  migrations/
tests/
```

## Hardening

- Python pinned and hashed (`pip-tools`), user-namespace Docker, seccomp profiles, resource limits.
- Safe HTML rendering, URL allowlists, robots compliance modes toggle, headless browser isolation.


## Added collectors (Kenya & East Africa focused)
- RSS multi-fetcher, with a curated **feeds/east_africa.yaml** (Standard, Capital FM, AllAfrica Kenya, Kenyamoja, etc.).
- Reddit collector for **r/Kenya** (and any other subreddit).
- YouTube channel RSS collector (use channel IDs of KE media houses).
- Wayback snapshot fetcher (for source tracking / change monitoring).


## Social media collectors (new)
- Twitter/X v2 search (requires `TWITTER_BEARER_TOKEN`)
- Facebook Pages posts (requires `FACEBOOK_GRAPH_TOKEN`)
- Instagram Business media (requires `IG_GRAPH_TOKEN`)
- Telegram updates (requires `TELEGRAM_BOT_TOKEN` and appropriate permissions)
- Discord channel messages (requires `DISCORD_BOT_TOKEN` + channel ID)
- Mastodon public timeline (instance URL + optional token)
- Bluesky author feed (public API)
- TikTok user posts (via yt-dlp metadata, no download)


## Auto-fallback chaining
Use `/social/twitter/search_auto` and `/social/reddit/top_auto` for primary→fallback→wayback chaining.

## Deep web crawler
`POST /crawl/deepweb` with `seeds` and `allow_domains` (allowlist required) will perform a polite BFS crawl with robots.txt respect and rate limiting.

## Onion/Tor crawler (safe-by-default)
`POST /crawl/onion` requires `allow_onion=true`, a running Tor SOCKS proxy (set `TOR_SOCKS_PROXY`), and explicit `seeds`. Only the seed domains are crawled.

> Legal & Safety: You are responsible for complying with laws and site terms. The system only crawls domains you allowlist. Onion crawling is disabled unless you explicitly enable it.


## Vision & Vector Enrichment
- **YOLOv8** (`/enrich/yolo`): object detection on images (default `yolov8n.pt`).
- **CLIP + FAISS**:
  - Index images: `/enrich/clip/index_images` (stores index in-memory, namespaced)
  - Text-to-image search: `/enrich/clip/search_text`

## Selenium Fallback
- `/collect/web_fallback?url=...&project_id=...&wait_css=.headline` tries `requests` then headless Chrome.

## Tor Service
- Compose spins up a `tor` container exposing SOCKS5 on `tor:9050`. Set `TOR_SOCKS_PROXY=socks5h://tor:9050` in `.env` for onion crawling.


## Reverse Image Search (exact + similar)
- **Index images** you want searchable:
  `POST /index/images/dir` with body `{ "image_paths": ["/data/images/a.jpg", "/data/images/b.jpg"] }`
  - Stores CLIP vectors to FAISS at `/data/faiss/images.index`
  - Stores hash metadata at `/data/faiss/images_meta.json`
- **Search by image upload**:
  `POST /search/image` (multipart file) → returns `exact_matches`, `near_duplicates` (phash) and `similar_matches` (CLIP cosine/IP score).


## Continuous Watchers (Images, Keywords, Usernames)
- **Create a watcher**:
  ```bash
  curl -X POST http://localhost:8080/watchers -H "Content-Type: application/json" -d '{
    "type": "keyword",
    "config": {"term":"Nairobi power outage","subreddits":["Kenya"], "nitter_instance":"https://nitter.net"},
    "interval_seconds": 1800
  }'
  ```
- **List watchers**: `GET /watchers`
- **Run once (manual)**: `POST /watchers/run_once`
- Scheduler service `watcher-scheduler` runs every `$WATCHER_TICK_SECONDS`.

### Alerts
- WhatsApp: set `TWILIO_*` env vars + `ALERTS_WHATSAPP_TO`
- Webhook: set `ALERT_WEBHOOK_URL` to your SIEM/receiver
