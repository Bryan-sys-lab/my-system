import time

def fetch_rss(query=None, limit=10):
    # simulate a hanging collector by sleeping longer than usual
    time.sleep(2.0)
    return [{"title": "hang-1"}]

def fetch_rss_quick(query=None, limit=10):
    return [{"title": "quick-after-hang"}]
