import pytest
from libs.common import config, fallback

def test_config_env_defaults(monkeypatch):
    # Edge: no env vars set
    monkeypatch.delenv('POSTGRES_USER', raising=False)
    monkeypatch.delenv('POSTGRES_PASSWORD', raising=False)
    monkeypatch.delenv('POSTGRES_DB', raising=False)
    monkeypatch.delenv('POSTGRES_HOST', raising=False)
    monkeypatch.delenv('POSTGRES_PORT', raising=False)
    assert 'postgresql' in config.POSTGRES_DSN

def test_run_with_fallbacks_all_fail():
    # Edge: all fallbacks fail
    def fail(): raise Exception('fail')
    result = fallback.run_with_fallbacks([('fail1', fail), ('fail2', fail)])
    assert result['data'] == []
    assert result['source'] == 'fail2'
