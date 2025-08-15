import pytest
from libs.crawlers import crawler, onion_crawler

def test_polite_crawl_extremes():
    # Edge: empty seeds
    result = crawler.polite_crawl([], allow_domains=set(), max_pages=1)
    assert result == []
    # Edge: negative max_pages
    with pytest.raises(Exception):
        crawler.polite_crawl(['http://example.com'], allow_domains=set(), max_pages=-1)

def test_onion_crawler_extremes():
    # Edge: empty seeds
    result = onion_crawler.crawl_onion([], allow_onion=True, max_pages=1)
    assert result == []
    # Edge: negative max_pages
    with pytest.raises(Exception):
        onion_crawler.crawl_onion(['http://exampleonion.onion'], allow_onion=True, max_pages=-1)
