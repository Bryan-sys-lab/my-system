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
    with pytest.raises(Exception):
        web_simple.fetch_url('not_a_url')
    # Edge: unreachable URL
    with pytest.raises(Exception):
        web_simple.fetch_url('http://localhost:9999')

def test_youtube_rss_channel_extremes():
    # Edge: invalid channel
    with pytest.raises(Exception):
        youtube_rss.fetch_channel('notarealchannelid')
