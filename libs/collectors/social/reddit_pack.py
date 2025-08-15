from libs.collectors.reddit import fetch_subreddit_json

def multi_subreddits(subreddits, limit=25):
    out = []
    for s in subreddits:
        out.extend(fetch_subreddit_json(s, limit=limit))
    return out
