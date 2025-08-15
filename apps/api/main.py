from fastapi import FastAPI, HTTPException, Body
from prometheus_client import Counter, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import PlainTextResponse
from libs.collectors.web_simple import fetch_url
from libs.collectors.rss import fetch_rss
from libs.enrichment.nlp import extract_entities
from libs.crypto.btc import address_txs
from libs.storage.db import SessionLocal
from libs.storage.models import Project, Source, Item, Alert
from sqlalchemy import select
import uuid
import os, io, json, hashlib
from fastapi import UploadFile, File
from libs.enrichment.hash_index import build_hash_meta, hamming, phash_file, sha256_file
import faiss
import numpy as np
from libs.enrichment.clip_embed import embed_images, embed_texts

from libs.collectors.web_fallback import fetch_with_fallback as web_fetch_with_fallback

from libs.enrichment.vision_yolov8 import detect_objects
from libs.enrichment.clip_embed import embed_images, embed_texts
from libs.enrichment.faiss_index import build_index as faiss_build_index, search as faiss_search

from libs.crawlers.crawler import polite_crawl
from libs.crawlers.onion_crawler import crawl_onion

from libs.common.fallback import run_with_fallbacks
from libs.collectors.social.nitter_search import nitter_search
from libs.collectors.reddit_old import old_reddit_top
from libs.collectors.wayback import latest_snapshot as wb_latest
from libs.collectors.wayback_fetch import fetch_wayback_text

from libs.collectors.social.twitter_v2 import search_recent as twitter_search_recent
from libs.collectors.social.facebook_pages import page_posts as fb_page_posts
from libs.collectors.social.instagram_business import user_media as ig_user_media
from libs.collectors.social.telegram import channel_updates as tg_channel_updates
from libs.collectors.social.discord import channel_messages as discord_channel_messages
from libs.collectors.social.mastodon import timeline as mastodon_timeline
from libs.collectors.social.bluesky import recent_by_actor as bsky_recent_by_actor
from libs.collectors.social.tiktok import user_posts as tiktok_user_posts
from libs.collectors.social.reddit_pack import multi_subreddits as reddit_multi

from fastapi import Query
from libs.collectors.rss_multi import fetch_many as rss_fetch_many
from libs.collectors.reddit import fetch_subreddit_json
from libs.collectors.youtube_rss import fetch_channel as youtube_fetch_channel
from libs.collectors.wayback import latest_snapshot
import yaml, os


app = FastAPI(title="b-search API", version="1.0.0")

REQS = Counter("api_requests_total", "Total API requests", ["endpoint"])
HEALTH = Gauge("app_health", "Health status")

@app.get("/healthz")
def healthz():
    HEALTH.set(1)
    return {"status":"ok"}

@app.get("/metrics")
def metrics():
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/projects")
def create_project(name: str = Body(..., embed=True)):
    REQS.labels("/projects").inc()
    db = SessionLocal()
    try:
        p = Project(id=uuid.uuid4(), name=name)
        db.add(p); db.commit()
        return {"id": str(p.id), "name": p.name}
    finally:
        db.close()

@app.get("/projects")
def list_projects():
    db = SessionLocal()
    try:
        rows = db.execute(select(Project)).scalars().all()
        return [{"id": str(r.id), "name": r.name} for r in rows]
    finally:
        db.close()

@app.post("/collect/web")
def collect_web(url: str = Body(..., embed=True), project_id: str = Body(..., embed=True)):
    REQS.labels("/collect/web").inc()
    data = fetch_url(url)
    db = SessionLocal()
    try:
        item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=data["text"], meta={"title": data["title"], "url": url})
        db.add(item); db.commit()
        ents = extract_entities(data["text"][:10000])
        return {"saved_item": str(item.id), "entities": ents}
    finally:
        db.close()

@app.get("/crypto/btc/{address}")
def btc_activity(address: str):
    REQS.labels("/crypto/btc").inc()
    try:
        txs = address_txs(address)
        return {"count": len(txs), "txs": txs[:10]}
    except Exception as e:
        raise HTTPException(400, str(e))


@app.post("/collect/rss-pack")
def collect_rss_pack(project_id: str = Body(..., embed=True), pack: str = Body("feeds/east_africa.yaml", embed=True)):
    REQS.labels("/collect/rss-pack").inc()
    # load list and fetch
    with open(pack, "r") as f:
        cfg = yaml.safe_load(f)
    feeds = [s["url"] for s in cfg.get("sources", []) if s.get("type") == "rss"]
    data = rss_fetch_many(feeds, per_feed_limit=20)
    db = SessionLocal()
    try:
        saved = []
        for it in data:
            item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=it.get("summary",""), meta=it)
            db.add(item); saved.append(str(item.id))
        db.commit()
        return {"saved": saved, "count": len(saved)}
    finally:
        db.close()

@app.get("/collect/reddit/{subreddit}")
def collect_reddit(subreddit: str, project_id: str):
    REQS.labels("/collect/reddit").inc()
    data = fetch_subreddit_json(subreddit)
    db = SessionLocal()
    try:
        saved = []
        for it in data:
            item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=it.get("title",""), meta=it)
            db.add(item); saved.append(str(item.id))
        db.commit()
        return {"saved": saved, "count": len(saved)}
    finally:
        db.close()

@app.get("/collect/youtube")
def collect_youtube(channel_id: str, project_id: str):
    REQS.labels("/collect/youtube").inc()
    data = youtube_fetch_channel(channel_id)
    db = SessionLocal()
    try:
        saved = []
        for it in data:
            item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=it.get("title",""), meta=it)
            db.add(item); saved.append(str(item.id))
        db.commit()
        return {"saved": saved, "count": len(saved)}
    finally:
        db.close()

@app.get("/collect/wayback")
def collect_wayback(url: str, project_id: str):
    REQS.labels("/collect/wayback").inc()
    snap = latest_snapshot(url)
    if not snap:
        return {"snapshot": None}
    db = SessionLocal()
    try:
        item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=snap["url"], meta=snap)
        db.add(item); db.commit()
        return {"saved_item": str(item.id), "snapshot": snap}
    finally:
        db.close()


@app.get("/social/twitter/search")
def social_twitter_search(q: str, project_id: str, max_results: int = 25):
    REQS.labels("/social/twitter/search").inc()
    data = twitter_search_recent(q, max_results=max_results)
    db = SessionLocal()
    try:
        saved = []
        for it in data:
            item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=it.get("text",""), meta=it)
            db.add(item); saved.append(str(item.id))
        db.commit()
        return {"count": len(saved), "saved": saved}
    finally:
        db.close()

@app.get("/social/facebook/page")
def social_facebook_page(page_id: str, project_id: str, limit: int = 25):
    REQS.labels("/social/facebook/page").inc()
    data = fb_page_posts(page_id, limit=limit)
    db = SessionLocal()
    try:
        saved = []
        for it in data:
            item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=it.get("message",""), meta=it)
            db.add(item); saved.append(str(item.id))
        db.commit()
        return {"count": len(saved), "saved": saved}
    finally:
        db.close()

@app.get("/social/instagram/user")
def social_instagram_user(ig_user_id: str, project_id: str, limit: int = 25):
    REQS.labels("/social/instagram/user").inc()
    data = ig_user_media(ig_user_id, limit=limit)
    db = SessionLocal()
    try:
        saved = []
        for it in data:
            item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=it.get("caption",""), meta=it)
            db.add(item); saved.append(str(item.id))
        db.commit()
        return {"count": len(saved), "saved": saved}
    finally:
        db.close()

@app.get("/social/telegram/channel")
def social_telegram_channel(chat_id: str, project_id: str, limit: int = 50):
    REQS.labels("/social/telegram/channel").inc()
    data = tg_channel_updates(chat_id, limit=limit)
    db = SessionLocal()
    try:
        saved = []
        for it in data:
            text = it.get("message", {}).get("text", "") if isinstance(it, dict) else str(it)
            item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=text, meta=it)
            db.add(item); saved.append(str(item.id))
        db.commit()
        return {"count": len(saved), "saved": saved}
    finally:
        db.close()

@app.get("/social/discord/channel")
def social_discord_channel(channel_id: str, project_id: str, limit: int = 50):
    REQS.labels("/social/discord/channel").inc()
    data = discord_channel_messages(channel_id, limit=limit)
    db = SessionLocal()
    try:
        saved = []
        for it in data:
            item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=it.get("content",""), meta=it)
            db.add(item); saved.append(str(item.id))
        db.commit()
        return {"count": len(saved), "saved": saved}
    finally:
        db.close()

@app.get("/social/mastodon/public")
def social_mastodon_public(instance_url: str, project_id: str, access_token: str = "", limit: int = 20):
    REQS.labels("/social/mastodon/public").inc()
    data = mastodon_timeline(instance_url, access_token, limit=limit)
    db = SessionLocal()
    try:
        saved = []
        for it in data:
            item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=it.get("content",""), meta=it)
            db.add(item); saved.append(str(item.id))
        db.commit()
        return {"count": len(saved), "saved": saved}
    finally:
        db.close()

@app.get("/social/bluesky/actor")
def social_bluesky_actor(handle: str, project_id: str, limit: int = 25):
    REQS.labels("/social/bluesky/actor").inc()
    data = bsky_recent_by_actor(handle, limit=limit)
    db = SessionLocal()
    try:
        saved = []
        for it in data:
            text = (it.get('post', {}) or {}).get('record', {}).get('text', '')
            item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=text, meta=it)
            db.add(item); saved.append(str(item.id))
        db.commit()
        return {"count": len(saved), "saved": saved}
    finally:
        db.close()

@app.get("/social/tiktok/user")
def social_tiktok_user(username: str, project_id: str, max_items: int = 20):
    REQS.labels("/social/tiktok/user").inc()
    data = tiktok_user_posts(username, max_items=max_items)
    db = SessionLocal()
    try:
        saved = []
        for it in data:
            title = it.get("title") or it.get("id") or ""
            item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=title, meta=it)
            db.add(item); saved.append(str(item.id))
        db.commit()
        return {"count": len(saved), "saved": saved}
    finally:
        db.close()

@app.post("/social/reddit/multi")
def social_reddit_multi(project_id: str = Body(..., embed=True), subreddits: list[str] = Body(..., embed=True)):
    REQS.labels("/social/reddit/multi").inc()
    data = reddit_multi(subreddits)
    db = SessionLocal()
    try:
        saved = []
        for it in data:
            item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=it.get("title",""), meta=it)
            db.add(item); saved.append(str(item.id))
        db.commit()
        return {"count": len(saved), "saved": saved}
    finally:
        db.close()


@app.get("/social/twitter/search_auto")
def social_twitter_search_auto(q: str, project_id: str, max_results: int = 25, nitter_instance: str = "https://nitter.net"):
    REQS.labels("/social/twitter/search_auto").inc()
    def _main():
        return twitter_search_recent(q, max_results=max_results)
    def _nitter():
        return nitter_search(nitter_instance, q, limit=max_results)
    # Wayback fallback: search query page snapshot
    def _wayback():
        snap = wb_latest(f"https://x.com/search?q={q}")
        if not snap: 
            return []
        doc = fetch_wayback_text(snap["url"])
        return [{"text": doc["text"][:1000], "wayback_url": doc["url"]}]
    result = run_with_fallbacks([("twitter_v2", _main), ("nitter", _nitter), ("wayback", _wayback)])
    data = result["data"]
    db = SessionLocal()
    try:
        saved = []
        for it in data:
            content = it.get("text") or it.get("title") or ""
            item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=content, meta={"source": result["source"], **it})
            db.add(item); saved.append(str(item.id))
        db.commit()
        return {"source": result["source"], "count": len(saved), "saved": saved, "errors": result.get("errors",[])}
    finally:
        db.close()

@app.get("/social/reddit/top_auto")
def social_reddit_top_auto(subreddit: str, project_id: str, limit: int = 25):
    REQS.labels("/social/reddit/top_auto").inc()
    def _json():
        return fetch_subreddit_json(subreddit, limit=limit)
    def _old():
        return old_reddit_top(subreddit, limit=limit)
    def _wayback():
        snap = wb_latest(f"https://www.reddit.com/r/{subreddit}/")
        if not snap:
            return []
        doc = fetch_wayback_text(snap["url"])
        return [{"title": doc["text"][:1000], "wayback_url": doc["url"]}]
    result = run_with_fallbacks([("reddit_json", _json), ("old_reddit", _old), ("wayback", _wayback)])
    data = result["data"]
    db = SessionLocal()
    try:
        saved = []
        for it in data:
            content = it.get("title") or it.get("text") or ""
            item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=content, meta={"source": result["source"], **it})
            db.add(item); saved.append(str(item.id))
        db.commit()
        return {"source": result["source"], "count": len(saved), "saved": saved, "errors": result.get("errors",[])}
    finally:
        db.close()


from typing import List

@app.post("/crawl/deepweb")
def crawl_deepweb(project_id: str = Body(..., embed=True), seeds: List[str] = Body(..., embed=True), allow_domains: List[str] = Body(..., embed=True), max_pages: int = Body(100, embed=True)):
    REQS.labels("/crawl/deepweb").inc()
    data = polite_crawl(seeds, allow_domains=set(allow_domains), max_pages=max_pages)
    db = SessionLocal()
    try:
        saved = []
        for it in data:
            item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=it.get("text",""), meta={"url": it.get("url")})
            db.add(item); saved.append(str(item.id))
        db.commit()
        return {"count": len(saved), "saved": saved}
    finally:
        db.close()

@app.post("/crawl/onion")
def crawl_onion_api(project_id: str = Body(..., embed=True), seeds: List[str] = Body(..., embed=True), allow_onion: bool = Body(False, embed=True), max_pages: int = Body(50, embed=True)):
    REQS.labels("/crawl/onion").inc()
    data = crawl_onion(seeds, allow_onion=allow_onion, max_pages=max_pages)
    db = SessionLocal()
    try:
        saved = []
        for it in data:
            item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=it.get("text",""), meta={"url": it.get("url")})
            db.add(item); saved.append(str(item.id))
        db.commit()
        return {"count": len(saved), "saved": saved}
    finally:
        db.close()


from typing import List
import numpy as np
import base64
import io

@app.post("/enrich/yolo")
def enrich_yolo(project_id: str = Body(..., embed=True), image_paths: List[str] = Body(..., embed=True), model_name: str = Body("yolov8n.pt", embed=True)):
    REQS.labels("/enrich/yolo").inc()
    dets = detect_objects(image_paths, model_name=model_name)
    db = SessionLocal()
    try:
        saved = []
        for it in dets:
            item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=f"YOLO detections for {it['image']}", meta=it)
            db.add(item); saved.append(str(item.id))
        db.commit()
        return {"count": len(saved), "saved": saved}
    finally:
        db.close()

# simple in-memory FAISS demo for image embeddings
_FAISS_CACHE = {}

@app.post("/enrich/clip/index_images")
def enrich_clip_index_images(namespace: str = Body(..., embed=True), image_paths: List[str] = Body(..., embed=True)):
    REQS.labels("/enrich/clip/index_images").inc()
    vecs = embed_images(image_paths)
    index = faiss_build_index(vecs)
    _FAISS_CACHE[namespace] = {"index": index, "paths": image_paths}
    return {"namespace": namespace, "count": len(image_paths)}

@app.post("/enrich/clip/search_text")
def enrich_clip_search_text(namespace: str = Body(..., embed=True), queries: List[str] = Body(..., embed=True), k: int = Body(5, embed=True)):
    REQS.labels("/enrich/clip/search_text").inc()
    if namespace not in _FAISS_CACHE:
        raise HTTPException(status_code=400, detail="namespace not indexed")
    vecq = embed_texts(queries)
    D, I = faiss_search(_FAISS_CACHE[namespace]["index"], vecq, k=k)
    results = []
    for qi, q in enumerate(queries):
        hits = [{"path": _FAISS_CACHE[namespace]["paths"][int(i)], "score": float(D[qi][hi])} for hi, i in enumerate(I[qi])]
        results.append({"query": q, "hits": hits})
    return {"namespace": namespace, "results": results}


@app.get("/collect/web_fallback")
def collect_web_fallback(url: str, project_id: str, wait_css: str = ""):
    REQS.labels("/collect/web_fallback").inc()
    res = web_fetch_with_fallback(url, wait_css=wait_css or None)
    db = SessionLocal()
    try:
        item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=res["data"].get("text",""), meta={"url": url, "source": res["source"]})
        db.add(item); db.commit()
        return {"saved": str(item.id), "source": res["source"]}
    finally:
        db.close()


@app.post("/batch/run")
def batch_run(
    project_id: str = Body(..., embed=True),
    rss: list[str] = Body(default=[], embed=True),
    twitter_handles: list[str] = Body(default=[], embed=True),
    facebook_pages: list[str] = Body(default=[], embed=True),
    instagram_ids: list[str] = Body(default=[], embed=True),
    telegram_chats: list[str] = Body(default=[], embed=True),
    discord_channels: list[str] = Body(default=[], embed=True),
    mastodon_instances: list[str] = Body(default=[], embed=True),
    bluesky_handles: list[str] = Body(default=[], embed=True),
    tiktok_users: list[str] = Body(default=[], embed=True),
    reddit_subreddits: list[str] = Body(default=[], embed=True),
    deepweb: dict = Body(default=None, embed=True),
    onion: dict = Body(default=None, embed=True),
    nitter_instance: str = Body(default="https://nitter.net", embed=True),
):
    REQS.labels("/batch/run").inc()
    db = SessionLocal()
    saved_ids = []
    meta_summary = {"rss":0,"twitter":0,"facebook":0,"instagram":0,"telegram":0,"discord":0,"mastodon":0,"bluesky":0,"tiktok":0,"reddit":0,"deepweb":0,"onion":0}

    def _save(content, meta):
        item = Item(id=uuid.uuid4(), project_id=uuid.UUID(project_id), content=content or "", meta=meta)
        db.add(item); saved_ids.append(str(item.id))

    try:
        # RSS packs: each entry in `rss` can be a YAML file path or a direct feed URL
        for entry in rss:
            try:
                if entry.endswith(".yaml") or entry.endswith(".yml"):
                    import yaml, pathlib
                    cfg = yaml.safe_load(pathlib.Path(entry).read_text())
                    feeds = cfg.get("feeds", [])
                else:
                    feeds = [entry]
                for f in rss_fetch_many(feeds):
                    _save(f.get("title",""), f)
                    meta_summary["rss"] += 1
            except Exception as e:
                continue

        # Twitter: try API then Nitter fallback
        for h in twitter_handles:
            q = f"from:{h.lstrip('@')}"
            data = []
            try:
                data = _tw_search(q, max_results=50)
                src = "twitter_v2"
            except Exception:
                try:
                    data = _tw_nitter(nitter_instance, q, limit=50)
                    src = "nitter"
                except Exception:
                    # Wayback fallback of search page
                    try:
                        snap = _wb_latest(f"https://x.com/search?q={q}")
                        if snap:
                            doc = _wb_fetch(snap["url"]); data = [{"text": doc["text"][:1000], "wayback_url": doc["url"]}]
                            src = "wayback"
                    except Exception:
                        data = []
                        src = "none"
            for it in data:
                content = it.get("text") or it.get("title") or ""
                _save(content, {"platform":"twitter","handle":h,"source":src, **it})
                meta_summary["twitter"] += 1

        # Facebook pages
        for pid in facebook_pages:
            try:
                posts = _fb_page(pid, limit=50)
                for it in posts:
                    _save(it.get("message",""), {"platform":"facebook","page":pid, **it})
                    meta_summary["facebook"] += 1
            except Exception:
                continue

        # Instagram (business IDs)
        for igid in instagram_ids:
            try:
                media = _ig_user(igid, limit=50)
                for it in media:
                    _save(it.get("caption",""), {"platform":"instagram","user":igid, **it})
                    meta_summary["instagram"] += 1
            except Exception:
                continue

        # Telegram chats (bot updates or channel where bot is admin)
        for chat in telegram_chats:
            try:
                ups = _tg_updates(chat, limit=100)
                for it in ups:
                    text = it.get("message",{}).get("text","") if isinstance(it, dict) else str(it)
                    _save(text, {"platform":"telegram","chat":chat, **it})
                    meta_summary["telegram"] += 1
            except Exception:
                continue

        # Discord channels
        for ch in discord_channels:
            try:
                msgs = _dc_messages(ch, limit=100)
                for it in msgs:
                    _save(it.get("content",""), {"platform":"discord","channel":ch, **it})
                    meta_summary["discord"] += 1
            except Exception:
                continue

        # Mastodon public timelines (instance URLs)
        for inst in mastodon_instances:
            try:
                tl = _masto_tl(inst, access_token="", limit=50)
                for it in tl:
                    _save(it.get("content",""), {"platform":"mastodon","instance":inst, **it})
                    meta_summary["mastodon"] += 1
            except Exception:
                continue

        # Bluesky handles
        for b in bluesky_handles:
            try:
                feed = _bsky_actor(b, limit=50)
                for it in feed:
                    text = (it.get('post',{}) or {}).get('record',{}).get('text','')
                    _save(text, {"platform":"bluesky","handle":b, **it})
                    meta_summary["bluesky"] += 1
            except Exception:
                continue

        # TikTok users
        for u in tiktok_users:
            try:
                vids = _tiktok_user(u, max_items=30)
                for it in vids:
                    _save(it.get("title") or it.get("id") or "", {"platform":"tiktok","user":u, **it})
                    meta_summary["tiktok"] += 1
            except Exception:
                continue

        # Reddit subreddits
        for sub in reddit_subreddits:
            posts = []
            try:
                posts = _reddit_json(sub, limit=50)
                src = "json"
            except Exception:
                try:
                    posts = _reddit_old(sub, limit=50)
                    src = "old"
                except Exception:
                    posts = []
                    src = "none"
            for it in posts:
                _save(it.get("title",""), {"platform":"reddit","subreddit":sub,"source":src, **it})
                meta_summary["reddit"] += 1

        # Deepweb crawl
        if deepweb:
            try:
                seeds = deepweb.get("seeds", [])
                allow_domains = set(deepweb.get("allow_domains", []))
                max_pages = int(deepweb.get("max_pages", 100))
                crawled = _deep_crawl(seeds, allow_domains=allow_domains, max_pages=max_pages)
                for it in crawled:
                    _save(it.get("text",""), {"crawl":"deepweb", **it})
                    meta_summary["deepweb"] += 1
            except Exception:
                pass

        # Onion crawl (requires Tor & allow_onion=True)
        if onion and onion.get("allow_onion"):
            try:
                seeds = onion.get("seeds", [])
                max_pages = int(onion.get("max_pages", 50))
                crawled = _onion_crawl(seeds, allow_onion=True, max_pages=max_pages)
                for it in crawled:
                    _save(it.get("text",""), {"crawl":"onion", **it})
                    meta_summary["onion"] += 1
            except Exception:
                pass

        db.commit()
        return {"saved": saved_ids, "counts": meta_summary}
    finally:
        db.close()


DATA_DIR = os.getenv("DATA_DIR", "/data")
FAISS_DIR = os.path.join(DATA_DIR, "faiss")
os.makedirs(FAISS_DIR, exist_ok=True)
INDEX_PATH = os.path.join(FAISS_DIR, "images.index")
META_PATH = os.path.join(FAISS_DIR, "images_meta.json")

def _load_index():
    if os.path.exists(INDEX_PATH):
        return faiss.read_index(INDEX_PATH)
    return None

def _save_index(index):
    faiss.write_index(index, INDEX_PATH)

def _load_meta():
    if os.path.exists(META_PATH):
        with open(META_PATH, "r") as f:
            return json.load(f)
    return []

def _save_meta(meta):
    with open(META_PATH, "w") as f:
        json.dump(meta, f, indent=2)

@app.post("/index/images/dir")
def index_images_from_dir(image_paths: list[str] = Body(..., embed=True)):
    REQS.labels("/index/images/dir").inc()
    # Build CLIP vectors
    vecs = embed_images(image_paths)
    # Persist index
    if vecs.size == 0:
        raise HTTPException(status_code=400, detail="no images")
    d = vecs.shape[1]
    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
        if index.d != d:
            # rebuild
            index = faiss.IndexFlatIP(d)
            index.add(vecs.astype('float32'))
        else:
            index.add(vecs.astype('float32'))
    else:
        index = faiss.IndexFlatIP(d)
        index.add(vecs.astype('float32'))
    _save_index(index)
    # Hash meta
    meta = _load_meta()
    meta += build_hash_meta(image_paths)
    _save_meta(meta)
    return {"indexed": len(image_paths), "total_index_size": index.ntotal}

@app.post("/search/image")
async def search_image(file: UploadFile = File(...), k: int = Body(12, embed=True), phash_hamming_max: int = Body(6, embed=True), clip_threshold: float = Body(0.25, embed=True)):
    REQS.labels("/search/image").inc()
    # Save uploaded file
    uploads_dir = os.path.join(DATA_DIR, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    buf = await file.read()
    up_path = os.path.join(uploads_dir, file.filename or "query.jpg")
    with open(up_path, "wb") as f:
        f.write(buf)

    # Exact / near-dup via hashes
    q_sha = sha256_file(up_path)
    q_phash = phash_file(up_path)
    meta = _load_meta()
    exact = []
    near = []
    for m in meta:
        if m.get("sha256") == q_sha:
            exact.append({"path": m["path"], "sha256": m["sha256"]})
        else:
            try:
                dist = hamming(q_phash, m.get("phash",""))
                if dist <= phash_hamming_max:
                    near.append({"path": m["path"], "hamming": dist})
            except Exception:
                continue
    near = sorted(near, key=lambda x: x["hamming"])

    # CLIP similarity (semantic)
    index = _load_index()
    similar = []
    if index is not None and index.ntotal > 0:
        vecq = embed_images([up_path])
        D, I = index.search(vecq.astype("float32"), k)
        scores = D[0].tolist()
        idxs = I[0].tolist()
        paths = [m["path"] for m in meta]
        for score, idx in zip(scores, idxs):
            if idx < 0 or idx >= len(paths):
                continue
            if score >= clip_threshold:
                similar.append({"path": paths[idx], "score": float(score)})
    return {
        "query": {"path": up_path, "sha256": q_sha, "phash": q_phash},
        "exact_matches": exact,
        "near_duplicates": near,
        "similar_matches": similar
    }


@app.post("/watchers")
def create_watcher(
    type: str = Body(...),
    config: dict = Body(...),
    interval_seconds: int = Body(3600),
    enabled: bool = Body(True)
):
    REQS.labels("/watchers").inc()
    db = SessionLocal()
    try:
        w = Watcher(id=uuid.uuid4(), type=type, config=config, interval_seconds=interval_seconds, enabled=enabled)
        db.add(w); db.commit()
        return {"id": str(w.id), "type": w.type, "interval_seconds": w.interval_seconds, "enabled": w.enabled}
    finally:
        db.close()

@app.get("/watchers")
def list_watchers():
    db = SessionLocal()
    try:
        ws = db.query(Watcher).all()
        return [{"id": str(w.id), "type": w.type, "interval_seconds": w.interval_seconds, "enabled": w.enabled, "last_run_at": w.last_run_at, "config": w.config} for w in ws]
    finally:
        db.close()

@app.post("/watchers/run_once")
def watchers_run_once():
    REQS.labels("/watchers/run_once").inc()
    from apps.workers.watchers import run_due_watchers as _run
    return _run()
