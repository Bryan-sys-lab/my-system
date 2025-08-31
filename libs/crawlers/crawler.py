import time, re, urllib.parse
from collections import deque
import requests
from bs4 import BeautifulSoup
from urllib import robotparser

DEFAULT_HEADERS = {"User-Agent": "b-search/1.0"}

def is_allowed(url: str, rp: robotparser.RobotFileParser) -> bool:
    try:
        return rp.can_fetch(DEFAULT_HEADERS["User-Agent"], url)
    except Exception:
        return True

def fetch(url: str, session: requests.Session = None, timeout: int = 20):
    s = session or requests.Session()
    r = s.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
    r.raise_for_status()
    return r.text

def extract_links(base_url: str, html: str):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = urllib.parse.urljoin(base_url, a["href"])
        links.add(href.split("#")[0])
    text = " ".join(t.get_text(" ", strip=True) for t in soup.find_all(["p","li","h1","h2","h3"]))
    return links, re.sub(r"\s+", " ", text)[:20000]

def polite_crawl(seeds, allow_domains=None, deny_patterns=None, max_pages=100, per_domain_delay=1.0, session=None):
    allow_domains = set(allow_domains or [])
    # Validate inputs for defensive behavior (tests expect exceptions on bad args)
    if max_pages is None or not isinstance(max_pages, int) or max_pages < 0:
        raise Exception("max_pages must be a non-negative integer")
    deny_patterns = [re.compile(p) for p in (deny_patterns or [])]
    visited = set()
    queue = deque(seeds)
    results = []
    robots_cache = {}

    def domain(url):
        return urllib.parse.urlparse(url).netloc

    while queue and len(results) < max_pages:
        url = queue.popleft()
        if url in visited: 
            continue
        d = domain(url)
        if allow_domains and d not in allow_domains:
            continue
        if any(p.search(url) for p in deny_patterns):
            continue

        # robots
        if d not in robots_cache:
            rp = robotparser.RobotFileParser()
            rp.set_url(urllib.parse.urljoin(f"http://{d}", "/robots.txt"))
            try:
                rp.read()
            except Exception:
                pass
            robots_cache[d] = rp
        else:
            rp = robots_cache[d]

        if not is_allowed(url, rp):
            continue

        try:
            html = fetch(url, session=session)
            links, text = extract_links(url, html)
            results.append({"url": url, "text": text})
            visited.add(url)
            for link in links:
                if allow_domains and domain(link) not in allow_domains: 
                    continue
                if link not in visited:
                    queue.append(link)
            time.sleep(per_domain_delay)
        except Exception:
            continue
    return results
