from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from libs.common.config import POSTGRES_DSN

engine = create_engine(POSTGRES_DSN, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()
