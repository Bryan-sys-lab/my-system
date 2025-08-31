import feedparser

def fetch_rss(url: str, limit: int = 25):
    feed = feedparser.parse(url)
    # feedparser sets `bozo` when parsing failed; surface as exception for
    # callers/tests that expect invalid URLs to raise.
    if getattr(feed, 'bozo', False):
        raise Exception('Invalid or malformed feed')
    items = []
    for e in feed.entries[:limit]:
        items.append({
            "title": getattr(e, "title", ""),
            "link": getattr(e, "link", ""),
            "summary": getattr(e, "summary", ""),
            "published": getattr(e, "published", ""),
        })
    return {"feed_title": getattr(feed.feed, "title", ""), "items": items}
