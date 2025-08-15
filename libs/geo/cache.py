from __future__ import annotations
import json
import time
from typing import Optional
import redis

class RedisCache:
    def __init__(self, url: str):
        self.client = redis.Redis.from_url(url, decode_responses=True)

    def get_json(self, key: str) -> Optional[dict]:
        val = self.client.get(key)
        if not val:
            return None
        try:
            return json.loads(val)
        except Exception:
            return None

    def set_json(self, key: str, value: dict, ttl: int = 86400):
        try:
            self.client.setex(key, ttl, json.dumps(value))
        except Exception:
            pass
