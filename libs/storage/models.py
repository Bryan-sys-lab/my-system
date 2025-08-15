import uuid
from sqlalchemy import Column, String, Text, JSON, TIMESTAMP, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from libs.storage.db import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
    sources = relationship("Source", back_populates="project", cascade="all, delete")
    items = relationship("Item", back_populates="project", cascade="all, delete")

class Source(Base):
    __tablename__ = "sources"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))
    type = Column(String, nullable=False)
    url = Column(Text)
    params = Column(JSON)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
    project = relationship("Project", back_populates="sources")

class Item(Base):
    __tablename__ = "items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id", ondelete="SET NULL"))
    content = Column(Text)
    meta = Column(JSON)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
    project = relationship("Project", back_populates="items")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"))
    level = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    payload = Column(JSON)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))


class Watcher(Base):
    __tablename__ = "watchers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String, nullable=False)  # image | keyword | username
    config = Column(JSONB, nullable=False, default=dict)
    interval_seconds = Column(Integer, nullable=False, default=3600)
    enabled = Column(Boolean, nullable=False, default=True)
    last_run_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class WatcherHit(Base):
    __tablename__ = "watcher_hits"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    watcher_id = Column(UUID(as_uuid=True), ForeignKey("watchers.id", ondelete="CASCADE"), index=True, nullable=False)
    fingerprint = Column(String, index=True)  # e.g., sha256 of content/url or media
    meta = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
