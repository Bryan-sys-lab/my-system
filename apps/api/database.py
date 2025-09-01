"""
Database utilities and session management for the B-Search API
"""
from contextlib import contextmanager
from typing import Generator
from sqlalchemy.orm import Session
from libs.storage.db import SessionLocal
from .exceptions import DatabaseError


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Yields:
        Session: SQLAlchemy database session

    Raises:
        DatabaseError: If session creation or cleanup fails
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise DatabaseError(
            f"Database operation failed: {str(e)}",
            operation="session_management",
            details={"error_type": e.__class__.__name__}
        )
    finally:
        session.close()


def safe_db_operation(operation_name: str):
    """
    Decorator for safe database operations.

    Args:
        operation_name: Name of the operation for error reporting

    Returns:
        Decorated function that handles database errors
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                with get_db_session() as session:
                    return func(session, *args, **kwargs)
            except DatabaseError:
                raise
            except Exception as e:
                raise DatabaseError(
                    f"Operation '{operation_name}' failed: {str(e)}",
                    operation=operation_name,
                    details={"error_type": e.__class__.__name__}
                )
        return wrapper
    return decorator


class DatabaseManager:
    """Manager class for database operations"""

    @staticmethod
    def create_item(session: Session, item_data: dict) -> dict:
        """Create a new item in the database"""
        from libs.storage.models import Item
        import uuid
        # Normalize None content values to empty string to match API
        # expectations in tests and to avoid storing nulls.
        content_val = item_data.get("content", "")
        if content_val is None:
            content_val = ""

        item = Item(
            id=uuid.uuid4(),
            project_id=item_data["project_id"],
            content=content_val,
            meta=item_data.get("meta", {})
        )
        try:
            session.add(item)
        except Exception as e:
            # Surface database add-time errors as DatabaseError so callers
            # can handle them consistently in API handlers and tests.
            from .exceptions import DatabaseError as _DBErr
            raise _DBErr(f"DB add failed: {str(e)}", operation="create_item")
        return {
            "id": str(item.id),
            "project_id": str(item.project_id),
            "content": item.content,
            "meta": item.meta
        }

    @staticmethod
    def get_project_by_id(session: Session, project_id: str):
        """Get project by ID"""
        from libs.storage.models import Project
        import uuid
        return session.query(Project).filter(Project.id == uuid.UUID(project_id)).first()

    @staticmethod
    def get_items_by_project(session: Session, project_id: str, limit: int = 100, offset: int = 0):
        """Get items for a project with pagination"""
        from libs.storage.models import Item
        import uuid
        from sqlalchemy import desc

        return session.query(Item).filter(
            Item.project_id == uuid.UUID(project_id)
        ).order_by(desc(Item.created_at)).offset(offset).limit(limit).all()

    @staticmethod
    def count_items_by_project(session: Session, project_id: str) -> int:
        """Count items for a project"""
        from libs.storage.models import Item
        import uuid
        from sqlalchemy import func

        return session.query(func.count(Item.id)).filter(
            Item.project_id == uuid.UUID(project_id)
        ).scalar()

    @staticmethod
    def get_all_projects(session: Session):
        """Get all projects"""
        from libs.storage.models import Project
        return session.query(Project).all()

    @staticmethod
    def create_project(session: Session, name: str) -> dict:
        """Create a new project"""
        from libs.storage.models import Project
        import uuid

        project = Project(id=uuid.uuid4(), name=name)
        session.add(project)
        return {"id": str(project.id), "name": project.name}

    @staticmethod
    def get_watcher_by_id(session: Session, watcher_id: str):
        """Get watcher by ID"""
        from libs.storage.models import Watcher
        import uuid
        return session.query(Watcher).filter(Watcher.id == uuid.UUID(watcher_id)).first()

    @staticmethod
    def get_all_watchers(session: Session):
        """Get all watchers"""
        from libs.storage.models import Watcher
        return session.query(Watcher).all()

    @staticmethod
    def create_watcher(session: Session, watcher_data: dict) -> dict:
        """Create a new watcher"""
        from libs.storage.models import Watcher
        import uuid

        watcher = Watcher(
            id=uuid.uuid4(),
            type=watcher_data["type"],
            config=watcher_data.get("config", {}),
            interval_seconds=watcher_data.get("interval_seconds", 3600),
            enabled=watcher_data.get("enabled", True)
        )
        session.add(watcher)
        return {
            "id": str(watcher.id),
            "type": watcher.type,
            "interval_seconds": watcher.interval_seconds,
            "enabled": watcher.enabled
        }