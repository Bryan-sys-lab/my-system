import requests

def recent_by_actor(handle: str, limit: int = 25):
    url = "https://public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed"
    params = {"actor": handle, "limit": limit}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    return data.get("feed", [])
