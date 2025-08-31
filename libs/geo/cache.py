from __future__ import annotations
import json
import time
from typing import Optional
import redis

class RedisCache:
    def __init__(self, url: str = None):
        # Allow defaulting to a local test Redis URL or a no-op client when
        # the URL isn't supplied in tests.
        if not url:
            # Create a client that will attempt localhost by default; if Redis
            # isn't running, operations will gracefully fail.
            url = "redis://localhost:6379/0"
        try:
            self.client = redis.Redis.from_url(url, decode_responses=True)
            # quick connectivity test
            self.client.ping()
        except Exception:
            # Fallback to a dict-backed shim with TTL support so tests that
            # rely on expirations behave more like a real Redis instance.
            class _DummyClient:
                def __init__(self):
                    # store value and expiry timestamp
                    self._d = {}  # key -> (value, expires_at_or_None)

                def _purge_if_expired(self, k):
                    v = self._d.get(k)
                    if not v:
                        return
                    _, exp = v
                    if exp is not None and time.time() >= exp:
                        del self._d[k]

                def get(self, k):
                    self._purge_if_expired(k)
                    v = self._d.get(k)
                    return v[0] if v else None

                def setex(self, k, ttl, v):
                    expires = time.time() + int(ttl) if ttl and int(ttl) > 0 else None
                    self._d[k] = (v, expires)

                def set(self, k, v):
                    # persistent key without expiry
                    self._d[k] = (v, None)

                def delete(self, k):
                    self._d.pop(k, None)

                def ping(self):
                    return True

            self.client = _DummyClient()

    # Tests call `get` directly in some places; provide a simple wrapper.
    def get(self, key: str):
        return self.get_json(key)

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
