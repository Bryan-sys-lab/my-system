import pytest
import os
import glob

def test_all_modules_import():
    # Try importing every .py file in libs, app/ml, apps/api, apps/workers, cli
    base_dirs = [
        'libs', 'app/ml', 'apps/api', 'apps/workers', 'cli'
    ]
    for base in base_dirs:
        for py in glob.glob(f'{base}/**/*.py', recursive=True):
            mod = py.replace('/', '.').replace('.py', '')
            try:
                __import__(mod)
            except Exception as e:
                pytest.fail(f'Import failed: {mod}: {e}')

def test_env_vars_present():
    # Check all required env vars are set (from .env.example)
    env_path = os.path.join(os.path.dirname(__file__), '../.env.example')
    if not os.path.exists(env_path):
        pytest.skip('.env.example not found')
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key = line.split('=',1)[0].strip()
                if key:
                    assert key in os.environ, f'Missing env var: {key}'
