import requests
from bs4 import BeautifulSoup

def old_reddit_top(subreddit: str, limit: int = 25, t: str = "day"):
    url = f"https://old.reddit.com/r/{subreddit}/top/?t={t}"
    headers = {"User-Agent": "b-search/1.0"}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    out = []
    for post in soup.select(".thing")[:limit]:
        title = post.get("data-title") or post.select_one("a.title").get_text(strip=True)
        link = post.get("data-url") or post.select_one("a.title")["href"]
        out.append({"title": title, "link": link})
    return out
