import os, requests

def page_posts(page_id: str, limit: int = 25):
    token = os.getenv("FACEBOOK_GRAPH_TOKEN","")
    if not token:
        raise RuntimeError("FACEBOOK_GRAPH_TOKEN not set")
    url = f"https://graph.facebook.com/v19.0/{page_id}/posts"
    params = {"limit": limit, "access_token": token}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json().get("data", [])
    return data
