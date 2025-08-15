import os, uuid
from celery import Celery
from prometheus_client import start_http_server, Gauge
from libs.collectors.web_simple import fetch_url
from libs.storage.db import SessionLocal
from libs.storage.models import Item
from libs.common.alerts import whatsapp

celery_app = Celery("bsearch", broker=os.getenv("REDIS_URL","redis://redis:6379/0"))

HEALTH = Gauge("workers_health", "Worker health gauge")

@celery_app.on_after_configure.connect
def setup_metrics(sender, **kwargs):
    start_http_server(9000)

@celery_app.task
def scrape_and_store(project_id: str, url: str):
    HEALTH.set(1)
    data = fetch_url(url)
    db = SessionLocal()
    try:
        item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=data["text"], meta={"title": data["title"], "url": url})
        db.add(item); db.commit()
        if len(data["text"]) > 50000:
            whatsapp(f"Large page scraped: {url}")
        return str(item.id)
    finally:
        db.close()


@celery_app.task
def deep_crawl(project_id: str, seeds: list, allow_domains: list, max_pages: int = 100):
    HEALTH.set(1)
    from libs.crawlers.crawler import polite_crawl
    data = polite_crawl(seeds, allow_domains=set(allow_domains), max_pages=max_pages)
    db = SessionLocal()
    try:
        import uuid as _uuid
        from libs.storage.models import Item
        ids = []
        for it in data:
            item = Item(id=_uuid.uuid4(), project_id=_uuid.UUID(project_id), content=it.get("text",""), meta={"url": it.get("url")})
            db.add(item); ids.append(str(item.id))
        db.commit()
        return ids
    finally:
        db.close()
