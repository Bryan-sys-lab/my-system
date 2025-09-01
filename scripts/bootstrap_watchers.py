#!/usr/bin/env python3
"""Bootstrap demo watchers by calling the running API.

This script POSTs a few sample watchers to the running server. It uses
the HTTP API so it works with the in-memory SQLite fallback used by the
server process (creating them directly in a separate process would not
persist to the server's in-memory DB).
"""
import argparse
import sys
import json
from urllib.parse import urljoin

try:
    import requests
except Exception:
    print("requests is required to run this script. Activate the project's venv and install requirements.")
    sys.exit(2)

DEMOS = [
    {
        "type": "keyword",
        "config": {"term": "Kenya", "nitter_instance": "https://nitter.net"},
        "interval_seconds": 3600,
        "enabled": True,
    },
    {
        "type": "username",
        "config": {"handles": ["@example_user"]},
        "interval_seconds": 1800,
        "enabled": True,
    },
    {
        "type": "image",
        "config": {"file": "sample.jpg", "k": 12},
        "interval_seconds": 7200,
        "enabled": True,
    },
]


def create_watcher(base_url: str, payload: dict):
    url = urljoin(base_url, "/watchers")
    r = requests.post(url, json=payload, timeout=10)
    try:
        r.raise_for_status()
    except Exception:
        print("Failed to create watcher:", r.status_code, r.text)
        return None
    try:
        return r.json()
    except Exception:
        return r.text


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="http://127.0.0.1:8000", help="Base URL for the running API")
    args = p.parse_args()
    created = []
    print("Creating demo watchers at", args.url)
    for d in DEMOS:
        res = create_watcher(args.url, d)
        print(json.dumps({"payload": d, "response": res}, default=str, indent=2))
        created.append(res)
    print("Done. Created %d watchers (responses above)." % len(created))


if __name__ == "__main__":
    main()
