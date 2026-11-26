"""共享测试夹具：每个测试用独立的内存 SQLite，不依赖本地 MySQL。"""

from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.session import init_models, make_engine


@pytest_asyncio.fixture
async def engine():
    """内存 SQLite 引擎；StaticPool 保证同一连接看到同一份数据。"""
    engine = make_engine("sqlite+aiosqlite:///:memory:")
    await init_models(engine)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def session(engine) -> AsyncIterator[AsyncSession]:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
