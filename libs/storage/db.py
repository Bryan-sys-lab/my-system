from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
from libs.common.config import POSTGRES_DSN

# Try to use the configured Postgres DSN; if the DB driver isn't available
# or Postgres isn't reachable (e.g. not running in local test env), fall back
# to SQLite in-memory so unit tests can run without an external DB.
engine = None
try:
	engine = create_engine(POSTGRES_DSN, pool_pre_ping=True, future=True)
	# Verify a connection can be established now; if not, fall back.
	try:
		with engine.connect() as conn:
			pass
	except Exception:
		engine = None
except Exception:
	engine = None

if engine is None:
	# Use a StaticPool and check_same_thread=False so the in-memory SQLite DB
	# is preserved across connections during the test run.
	engine = create_engine(
		"sqlite:///:memory:",
		connect_args={"check_same_thread": False},
		poolclass=StaticPool,
		future=True,
	)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def init_db(force: bool = False):
	"""Create all tables for tests/dev when using the SQLite fallback.

	By default this only runs when the engine is SQLite (i.e., the Postgres
	connection wasn't available). Pass force=True to run unconditionally.
	"""
	try:
		is_sqlite = engine.url.get_backend_name() == 'sqlite'
	except Exception:
		is_sqlite = False
	if is_sqlite or force:
		Base.metadata.create_all(engine)
		return True
	return False
