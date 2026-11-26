"""异步数据库会话。"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

_engine = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = create_async_engine(get_settings().sqlalchemy_url, pool_pre_ping=True)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with get_session_factory()() as session:
        yield session


async def init_models() -> None:
    """按 ORM 元数据建表（v1 简化方案；生产建议用迁移工具）。"""
    from app.db.base import Base
    from app.models import entities  # noqa: F401  确保模型已注册

    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
