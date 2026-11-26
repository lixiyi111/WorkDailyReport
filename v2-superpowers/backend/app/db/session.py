"""异步数据库引擎与会话。

生产环境走 MySQL（aiomysql），测试环境走内存 SQLite（aiosqlite）。
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings
from app.models.entities import Base

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def make_engine(url: str) -> AsyncEngine:
    """按连接串创建引擎；内存 SQLite 使用 StaticPool 保持同一份数据。"""
    options: dict[str, Any] = {"echo": False, "pool_pre_ping": True}
    if url.startswith("sqlite+aiosqlite:///:memory:"):
        options["poolclass"] = StaticPool
        options["connect_args"] = {"check_same_thread": False}
    return create_async_engine(url, **options)


def get_engine() -> AsyncEngine:
    """进程内懒加载的生产引擎。"""
    global _engine
    if _engine is None:
        _engine = make_engine(get_settings().database_url)
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """进程内懒加载的会话工厂。"""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _session_factory


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI 依赖：每个请求一个会话。"""
    async with get_session_factory()() as session:
        yield session


async def init_models(engine: AsyncEngine | None = None) -> None:
    """建表；生产环境也可用 sql/schema.sql 显式建表。"""
    target = engine or get_engine()
    async with target.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_engine() -> None:
    """应用关闭时释放连接池。"""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None
