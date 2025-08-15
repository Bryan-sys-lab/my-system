import requests
from bs4 import BeautifulSoup

def old_reddit_top(subreddit: str, limit: int = 50):
    url = f"https://old.reddit.com/r/{subreddit}/top/?sort=top&t=day"
    headers = {"User-Agent": "b-search/1.0 (https://example.local)"}
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    posts = []
    for post in soup.select("div.thing")[:limit]:
        title = post.select_one("a.title")
        if not title:
            continue
        posts.append({
            "title": title.get_text(strip=True),
            "permalink": post.get("data-permalink"),
            "score": post.get("data-score"),
            "author": post.get("data-author"),
        })
    return posts
