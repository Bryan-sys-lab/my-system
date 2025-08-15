import pytest
from libs.storage import db, models

def test_db_engine_exists():
    assert hasattr(db, 'engine')
    assert hasattr(db, 'SessionLocal')
    assert hasattr(db, 'Base')

def test_models_classes():
    for cls in ['Project', 'Source', 'Item', 'Alert', 'Watcher', 'WatcherHit']:
        assert hasattr(models, cls)
