from libs.crawlers.tor_client import tor_session
from libs.crawlers.crawler import polite_crawl

def crawl_onion(seeds, allow_onion=True, max_pages=50, per_domain_delay=2.0):
    if not allow_onion:
        raise RuntimeError("Onion crawling disabled by config")
    s = tor_session()
    # Allow domains inferred from seeds
    allow_domains = list({__import__("urllib.parse").urlparse(u).netloc for u in seeds})
    return polite_crawl(seeds, allow_domains=allow_domains, max_pages=max_pages, per_domain_delay=per_domain_delay, session=s)
