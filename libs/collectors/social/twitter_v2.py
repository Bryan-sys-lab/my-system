import os, requests

def search_recent(query: str, max_results: int = 25):
    token = os.getenv("TWITTER_BEARER_TOKEN","")
    if not token:
        raise RuntimeError("TWITTER_BEARER_TOKEN not set")
    url = "https://api.x.com/2/tweets/search/recent"
    params = {"query": query, "max_results": min(max_results, 100), "tweet.fields": "created_at,author_id,public_metrics"}
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get(url, params=params, headers=headers, timeout=30)
    r.raise_for_status()
    return r.json().get("data", [])
