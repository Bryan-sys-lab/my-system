import time, re
import requests
from bs4 import BeautifulSoup

def fetch_url(url: str, timeout=20):
    headers = {"User-Agent": "b-search/1.0 (+https://example.local)"}
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    title = (soup.title.text.strip() if soup.title else "")
    text = " ".join(t.get_text(" ", strip=True) for t in soup.find_all(["p","li","h1","h2","h3"]))
    return {
        "title": title,
        "text": re.sub(r"\s+", " ", text)[:20000],
        "status": r.status_code,
        "url": url,
        "fetched_at": time.time(),
    }
