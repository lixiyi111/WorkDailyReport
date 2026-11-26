"""初始化 MySQL 表结构：python -m scripts.init_db"""

import asyncio

from app.core.logging import setup_logging
from app.db.session import init_models


async def main() -> None:
    setup_logging()
    await init_models()
    print("数据库表已创建")


if __name__ == "__main__":
    asyncio.run(main())
