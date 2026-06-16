import threading
import logging
from sqlalchemy import create_engine, Column, String, ForeignKey, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase, declared_attr, Session
from sqlalchemy.pool import NullPool

from app.config import settings

logger = logging.getLogger("ma_dd.database")

_db_url = settings.database_url
if _db_url.startswith("postgresql://") and "+" not in _db_url.split("://")[0]:
    _db_url = _db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

_is_sqlite = "sqlite" in _db_url

if _is_sqlite:
    logger.warning("─" * 50)
    logger.warning("  SQLite DETECTED — NOT for production use!")
    logger.warning("  SQLite can corrupt data under concurrent writes.")
    logger.warning("  Set DATABASE_URL to PostgreSQL before deploying.")
    logger.warning("  Example: DATABASE_URL=postgresql+psycopg://user:pass@host:5432/ma_dd")
    logger.warning("─" * 50)

_sqlite_args = {"check_same_thread": False, "timeout": 30} if _is_sqlite else {}

if _is_sqlite:
    engine = create_engine(_db_url, connect_args=_sqlite_args, poolclass=NullPool)
else:
    engine = create_engine(
        _db_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def enable_sqlite_wal():
    """Enable WAL mode for SQLite — safer concurrent reads."""
    if not _is_sqlite:
        return
    try:
        with engine.connect() as conn:
            conn.execute(event.dbapi_connection, lambda conn: conn.execute("PRAGMA journal_mode=WAL"))
            conn.execute(event.dbapi_connection, lambda conn: conn.execute("PRAGMA busy_timeout=30000"))
            conn.execute(event.dbapi_connection, lambda conn: conn.execute("PRAGMA foreign_keys=ON"))
        logger.info("SQLite WAL mode enabled — better concurrent read performance")
    except Exception:
        pass


class Base(DeclarativeBase):
    pass


# ── Tenant isolation ──────────────────────────────────────────────

_current_org_tls = threading.local()
_default_org_id: str | None = None


def get_current_org() -> str | None:
    return getattr(_current_org_tls, "org_id", None)


def set_current_org(org_id: str | None) -> None:
    _current_org_tls.org_id = org_id


def set_default_org(org_id: str) -> None:
    global _default_org_id
    _default_org_id = org_id


def get_default_org() -> str | None:
    return _default_org_id


class TenantMixin:
    @declared_attr
    def organization_id(cls):
        return Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)


_tenant_filter_enabled = True


def disable_tenant_filter():
    global _tenant_filter_enabled
    _tenant_filter_enabled = False


def enable_tenant_filter():
    global _tenant_filter_enabled
    _tenant_filter_enabled = True


@event.listens_for(Session, "do_orm_execute")
def _tenant_filter(execute_state):
    if not _tenant_filter_enabled:
        return
    org_id = get_current_org()
    if org_id is None:
        return
    if not execute_state.is_select:
        return
    try:
        for col_desc in execute_state.statement.column_descriptions:
            entity = col_desc.get("entity")
            if entity is not None and hasattr(entity, "organization_id"):
                execute_state.statement = execute_state.statement.where(entity.organization_id == org_id)
                return
    except Exception:
        pass


@event.listens_for(Session, "before_flush")
def _tenant_flush(session, flush_context, instances):
    org_id = get_current_org() or get_default_org()
    if org_id is None:
        return
    for instance in list(session.new) + list(session.dirty):
        if hasattr(instance, "organization_id") and instance.organization_id is None:
            instance.organization_id = org_id


# ── Session / init ───────────────────────────────────────────────


def init_db():
    import app.models
    Base.metadata.create_all(bind=engine)
    enable_sqlite_wal()
    _migrate_schema()


def _migrate_schema():
    try:
        from sqlalchemy import text
        dialect = engine.dialect.name
        if dialect == "sqlite":
            return
        for col, col_type in [
            ("plan", "VARCHAR(32) DEFAULT 'free'"),
            ("deal_count", "INTEGER DEFAULT 0"),
            ("user_count", "INTEGER DEFAULT 0"),
            ("document_count", "INTEGER DEFAULT 0"),
            ("storage_used_mb", "FLOAT DEFAULT 0"),
        ]:
            try:
                with engine.begin() as conn:
                    conn.execute(text(f"ALTER TABLE organizations ADD COLUMN {col} {col_type}"))
            except Exception:
                pass
    except Exception:
        pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
