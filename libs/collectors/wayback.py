import requests

def latest_snapshot(url: str):
    api = "http://archive.org/wayback/available"
    r = requests.get(api, params={"url": url}, timeout=20)
    r.raise_for_status()
    j = r.json()
    snaps = j.get("archived_snapshots", {})
    closest = snaps.get("closest")
    if not closest:
        return None
    return {"url": closest.get("url"), "timestamp": closest.get("timestamp")}
