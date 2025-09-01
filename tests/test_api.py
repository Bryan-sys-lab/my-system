import pytest
from fastapi.testclient import TestClient
from apps.api.main import app

client = TestClient(app)

def test_healthz():
    resp = client.get('/healthz')
    assert resp.status_code == 200
    assert resp.json()['status'] in ('ok', 'healthy')

def test_metrics():
    resp = client.get('/metrics')
    assert resp.status_code == 200
    assert 'api_requests_total' in resp.text

def test_projects_extremes():
    # Edge: create project with empty name
    resp = client.post('/projects', json={'name': ''})
    assert resp.status_code == 200 or resp.status_code == 422
    # Edge: list projects
    resp = client.get('/projects')
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
