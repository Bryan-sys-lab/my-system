import pytest
from libs.collectors import reddit, reddit_old, rss, rss_multi, wayback, wayback_fetch, web_simple, web_fallback, youtube_rss

def test_reddit_fetch_subreddit_json_extremes():
    # Edge: non-existent subreddit
    with pytest.raises(Exception):
        reddit.fetch_subreddit_json('thissubdoesnotexistforsure1234567890', limit=1)
    # Edge: zero limit
    assert reddit.fetch_subreddit_json('python', limit=0) == []
    # Edge: very high limit (should cap or not error)
    result = reddit.fetch_subreddit_json('python', limit=1000)
    assert isinstance(result, list)

def test_reddit_old_top_extremes():
    # Edge: non-existent subreddit
    with pytest.raises(Exception):
        reddit_old.old_reddit_top('thissubdoesnotexistforsure1234567890', limit=1)
    # Edge: zero limit
    assert reddit_old.old_reddit_top('python', limit=0) == []
    # Edge: very high limit
    result = reddit_old.old_reddit_top('python', limit=1000)
    assert isinstance(result, list)

def test_rss_fetch_extremes():
    # Edge: invalid URL
    with pytest.raises(Exception):
        rss.fetch_rss('http://notarealurl.abc')
    # Edge: valid but empty feed
    # (skip, as most feeds will not be empty)

def test_wayback_latest_snapshot_extremes():
    # Edge: invalid URL
    assert wayback.latest_snapshot('not_a_url') is None
    # Edge: valid but no snapshot
    assert wayback.latest_snapshot('http://example.com/thispagedoesnotexist1234567890') is None

def test_web_simple_fetch_url_extremes():
    # Edge: invalid URL
    result = web_simple.fetch_url('not_a_url')
    assert 'error' in result and result['error']
    # Edge: unreachable URL
    result = web_simple.fetch_url('http://localhost:9999')
    assert 'error' in result and result['error']

def test_web_simple_fetch_url_features():
    # Use a simple, reliable page
    url = 'https://example.com/'
    result = web_simple.fetch_url(url)
    assert 'title' in result and 'Example Domain' in result['title']
    assert 'text' in result and 'Example Domain' in result['text']
    # Test link extraction
    result_links = web_simple.fetch_url(url, extract_links=True)
    assert 'links' in result_links and any('example.com' in l for l in result_links['links'])
    # Test raw HTML return
    result_html = web_simple.fetch_url(url, return_html=True)
    assert 'html' in result_html and '<html' in result_html['html'].lower()
    # Test custom tag extraction (should still find text)
    result_tags = web_simple.fetch_url(url, extract_tags=['h1'])
    assert 'Example Domain' in result_tags['text']

def test_youtube_rss_channel_extremes():
    # Edge: invalid channel
    with pytest.raises(Exception):
        youtube_rss.fetch_channel('notarealchannelid')
