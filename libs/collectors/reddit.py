import requests

def fetch_subreddit_json(subreddit: str, limit: int = 50, t: str = "day"):
    headers = {"User-Agent": "b-search/1.0 (https://example.local)"}
    url = f"https://www.reddit.com/r/{subreddit}/top.json?t={t}&limit={limit}"
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    data = r.json()
    items = []
    for c in data.get("data", {}).get("children", []):
        d = c.get("data", {})
        items.append({
            "title": d.get("title"),
            "permalink": "https://www.reddit.com" + d.get("permalink", ""),
            "score": d.get("score"),
            "created_utc": d.get("created_utc"),
            "author": d.get("author"),
        })
    return items
