"""异步重试：指数退避，最多 attempts 次。"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable


async def retry_async[T](
    operation: Callable[[], Awaitable[T]],
    *,
    attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 8.0,
) -> T:
    """执行 operation，失败按指数退避重试；耗尽后抛出最后一次异常。"""
    if attempts < 1:
        raise ValueError("attempts must be >= 1")

    for attempt in range(1, attempts + 1):
        try:
            return await operation()
        except Exception:
            if attempt == attempts:
                raise
            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            if delay > 0:
                await asyncio.sleep(delay)

    raise RuntimeError("retry exhausted")  # pragma: no cover
