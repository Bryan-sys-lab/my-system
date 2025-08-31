import os
import time
import json

from libs.collectors.run_all import run_all_collectors, run_all_stream


def test_run_all_basic():
    # Run only the local test collectors
    res = run_all_collectors(None, 5, whitelist=["libs.collectors._tests.dummy_quick", "libs.collectors._tests.dummy_slow"], timeout=5, max_workers=4, collector_timeout=1.0, retries=1)
    assert isinstance(res, dict)
    assert "libs.collectors._tests.dummy_quick" in res
    assert res["libs.collectors._tests.dummy_quick"]["ok"] is True
    assert len(res["libs.collectors._tests.dummy_quick"]["records"]) >= 1


def test_run_all_stream():
    seen = {}
    for mod, info in run_all_stream(None, 5, whitelist=["libs.collectors._tests.dummy_quick", "libs.collectors._tests.dummy_slow"], timeout=5, max_workers=4, collector_timeout=1.0, retries=1):
        seen[mod] = info
    assert "libs.collectors._tests.dummy_quick" in seen
    assert "libs.collectors._tests.dummy_slow" in seen


def test_timeouts_and_retries():
    # Ensure hanging collector times out and retries can be applied
    res = run_all_collectors(None, 5, whitelist=["libs.collectors._tests.dummy_hang", "libs.collectors._tests.dummy_quick"], timeout=5, max_workers=2, collector_timeout=0.2, retries=2, backoff=0.01)
    # Hanging collector should have errored due to timeout
    hang = res.get("libs.collectors._tests.dummy_hang")
    assert hang is not None
    assert hang["ok"] is False
    assert "timed out" in hang["error"].lower() or "timeout" in hang["error"].lower()


def test_sse_format(monkeypatch):
    from fastapi.testclient import TestClient
    from apps.api.main import app

    monkeypatch.setenv("RUN_ALL_SECRET", "test-secret")
    client = TestClient(app)
    body = {"secret": "test-secret", "query": "x", "limit": 2, "whitelist": ["libs.collectors._tests.dummy_quick", "libs.collectors._tests.dummy_slow"], "collector_workers": 2, "collector_timeout": 1.0}
    with client.stream('POST', "/collect/run_all/stream", json=body) as r:
        assert r.status_code == 200
        it = r.iter_lines()
        first = next(it)
        # SSE framing: should start with 'event: result' then 'data: {...}'
        # read two lines from the same iterator
        lines = [first]
        lines.append(next(it))
    assert "event: result" in lines[0] or "event: start" in lines[0] or "data:" in lines[0]


def test_api_streaming_endpoint(monkeypatch):
    # Start a TestClient and call the streaming endpoint
    from fastapi.testclient import TestClient
    from apps.api.main import app

    monkeypatch.setenv("RUN_ALL_SECRET", "test-secret")
    client = TestClient(app)
    body = {"secret": "test-secret", "query": "x", "limit": 2, "whitelist": ["libs.collectors._tests.dummy_quick", "libs.collectors._tests.dummy_slow"], "collector_workers": 2, "collector_timeout": 1.0}
    modules = set()
    with client.stream('POST', "/collect/run_all/stream", json=body) as r:
        assert r.status_code == 200
        for line in r.iter_lines():
            if not line:
                continue
            # Only parse 'data:' lines
            if line.startswith('data:'):
                payload = line[len('data:'):].lstrip()
                obj = json.loads(payload)
                if isinstance(obj, dict) and obj.get('module'):
                    modules.add(obj.get("module"))
    assert "libs.collectors._tests.dummy_quick" in modules
    assert "libs.collectors._tests.dummy_slow" in modules


def test_process_isolation_flag(monkeypatch):
    # Verify the API accepts use_processes and the stream still works
    from fastapi.testclient import TestClient
    from apps.api.main import app

    monkeypatch.setenv("RUN_ALL_SECRET", "test-secret")
    client = TestClient(app)
    body = {"secret": "test-secret", "query": "x", "limit": 2, "whitelist": ["libs.collectors._tests.dummy_quick", "libs.collectors._tests.dummy_hang"], "collector_workers": 2, "collector_timeout": 0.2, "use_processes": True}
    modules = set()
    with client.stream('POST', "/collect/run_all/stream", json=body) as r:
        assert r.status_code == 200
        for line in r.iter_lines():
            if not line:
                continue
            if line.startswith('data:'):
                payload = line[len('data:'):].lstrip()
                obj = json.loads(payload)
                if isinstance(obj, dict) and obj.get('module'):
                    modules.add(obj.get('module'))

    assert "libs.collectors._tests.dummy_quick" in modules
    assert "libs.collectors._tests.dummy_hang" in modules
