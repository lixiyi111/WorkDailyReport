"""本地演示：SQLite + Mock 数据，跑通采集 → 生成 → 推送。

运行：python -m scripts.demo
"""

import asyncio
from datetime import date, timedelta
from pathlib import Path

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.base import Base
from app.models import entities  # noqa: F401  确保模型注册
from app.services.demo import run_demo


async def main() -> None:
    Path("data").mkdir(exist_ok=True)
    engine = create_async_engine("sqlite+aiosqlite:///./data/demo.db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        result, team = await run_demo(session, date.today() - timedelta(days=1))
        print("运行结果：", result)
        if team:
            print("\n" + team.content_md)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
