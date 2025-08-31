import time

def fetch_rss(query=None, limit=10):
    # simulate slow collector
    time.sleep(0.2)
    return [{"title": "slow-1"}]

def fetch_rss_error(query=None, limit=10):
    time.sleep(0.05)
    raise RuntimeError("simulated error")
