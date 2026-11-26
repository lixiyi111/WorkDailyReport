"""共享测试夹具：每个测试用独立的内存 SQLite，不依赖本地 MySQL。"""

from collections.abc import AsyncIterator

import httpx
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.session import get_session, init_models, make_engine
from app.main import app
from app.models.entities import AppUser
from app.services.auth import hash_password


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


@pytest_asyncio.fixture
async def client(session) -> AsyncIterator[httpx.AsyncClient]:
    """未登录的 API 客户端；测试可自行加 Authorization 头。"""

    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as http:
        yield http
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def admin_client(client, session) -> AsyncIterator[httpx.AsyncClient]:
    """已登录管理员的 API 客户端。"""
    session.add(
        AppUser(
            username="admin",
            password_hash=hash_password("admin123"),
            role="admin",
        )
    )
    await session.commit()
    response = await client.post(
        "/api/auth/login", json={"username": "admin", "password": "admin123"}
    )
    client.headers["Authorization"] = f"Bearer {response.json()['access_token']}"
    yield client

