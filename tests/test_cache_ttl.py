import time
from libs.geo.cache import RedisCache


def test_setex_and_expiry():
    c = RedisCache(url=None)
    # ensure using dummy client
    c.set_json('k1', {'v': 1}, ttl=1)
    v = c.get_json('k1')
    assert v == {'v': 1}
    time.sleep(1.2)
    v2 = c.get_json('k1')
    assert v2 is None


def test_set_and_delete():
    c = RedisCache(url=None)
    c.set_json('k2', {'v': 2}, ttl=0)
    assert c.get_json('k2') == {'v': 2}
    # delete via underlying client if available
    try:
        c.client.delete('k2')
    except Exception:
        pass
    assert c.get_json('k2') is None
