from typing import List, Dict
import time
import feedparser

def fetch_many(feeds: List[str], per_feed_limit: int = 25) -> List[Dict]:
    out = []
    for url in feeds:
        feed = feedparser.parse(url)
        items = []
        for e in feed.entries[:per_feed_limit]:
            items.append({
                "title": getattr(e, "title", ""),
                "link": getattr(e, "link", ""),
                "summary": getattr(e, "summary", ""),
                "published": getattr(e, "published", ""),
                "source": url,
            })
        out.extend(items)
        time.sleep(0.1)
    return out
