import os, requests

def user_media(ig_user_id: str, limit: int = 25):
    token = os.getenv("IG_GRAPH_TOKEN","")
    if not token:
        raise RuntimeError("IG_GRAPH_TOKEN not set")
    url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
    params = {"fields": "id,caption,media_type,media_url,permalink,timestamp", "limit": limit, "access_token": token}
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("data", [])
