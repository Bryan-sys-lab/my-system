import requests

def oembed(video_url: str):
    r = requests.get("https://www.youtube.com/oembed", params={"url": video_url, "format": "json"}, timeout=20)
    r.raise_for_status()
    return r.json()
