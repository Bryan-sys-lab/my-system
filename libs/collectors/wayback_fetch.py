import requests
from bs4 import BeautifulSoup

def fetch_wayback_text(snapshot_url: str):
    r = requests.get(snapshot_url, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    text = " ".join(t.get_text(" ", strip=True) for t in soup.find_all(["p","li","h1","h2","h3"]))[:20000]
    return {"url": snapshot_url, "text": text}
