import requests

def timeline(instance_url: str, access_token: str, limit: int = 20):
    url = instance_url.rstrip('/') + "/api/v1/timelines/public"
    headers = {"Authorization": f"Bearer {access_token}"} if access_token else {}
    params = {"limit": limit}
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json()
