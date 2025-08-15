import requests
from bs4 import BeautifulSoup

def nitter_search(instance: str, query: str, limit: int = 20):
    base = instance.rstrip('/')
    url = f"{base}/search?f=tweets&q={requests.utils.quote(query)}&since=&until=&near="
    headers = {"User-Agent": "b-search/1.0"}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    out = []
    for art in soup.select("article")[:limit]:
        text = " ".join([t.get_text(" ", strip=True) for t in art.select(".tweet-content media-body, .tweet-content")])
        link = art.select_one("a.status-link")
        href = link["href"] if link else ""
        out.append({"text": text, "url": base + href})
    return out
