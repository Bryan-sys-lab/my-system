import pytest
from libs.collectors import youtube_rss

# Replace with a real channel ID for integration tests, or mock requests for unit tests
def test_fetch_channel_basic():
    # This should always return a list or error dict
    result = youtube_rss.fetch_channel("UC_x5XG1OV2P6uZZ5FSM9Ttw", max_items=2)  # Google Developers
    assert isinstance(result, (list, dict))
    if isinstance(result, list):
        assert len(result) <= 2
        for item in result:
            assert "title" in item and "link" in item and "published" in item
            assert "yt_video_id" in item
    else:
        assert "error" in result

def test_fetch_channel_error():
    # Invalid channel should return error
    result = youtube_rss.fetch_channel("notarealchannelid1234567890")
    assert isinstance(result, dict) and "error" in result

@pytest.mark.asyncio
async def test_fetch_channel_async_basic():
    result = await youtube_rss.fetch_channel_async("UC_x5XG1OV2P6uZZ5FSM9Ttw", max_items=1)
    assert isinstance(result, (list, dict))
    if isinstance(result, list):
        assert len(result) == 1
        assert "title" in result[0] and "link" in result[0]
    else:
        assert "error" in result

def test_fetch_channel_extra_fields():
    result = youtube_rss.fetch_channel("UC_x5XG1OV2P6uZZ5FSM9Ttw", max_items=1, extract_fields=["media:group"])
    assert isinstance(result, (list, dict))
    if isinstance(result, list) and result:
        assert "media:group" in result[0]

def test_fetch_channel_return_raw_tree():
    raw = youtube_rss.fetch_channel("UC_x5XG1OV2P6uZZ5FSM9Ttw", return_raw=True)
    assert isinstance(raw, dict) and "raw" in raw
    tree = youtube_rss.fetch_channel("UC_x5XG1OV2P6uZZ5FSM9Ttw", return_tree=True)
    assert isinstance(tree, dict) and "tree" in tree
