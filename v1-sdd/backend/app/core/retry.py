"""异步重试工具：指数退避 + 抖动。"""

import asyncio
import random
from collections.abc import Awaitable, Callable


async def retry_async[T](
    fn: Callable[[], Awaitable[T]],
    *,
    attempts: int = 3,
    base_delay: float = 0.5,
    retry_on: tuple[type[BaseException], ...] = (Exception,),
) -> T:
    """执行 fn，失败时按指数退避重试；耗尽后抛出最后一次异常。"""
    last_error: BaseException | None = None
    for attempt in range(1, attempts + 1):
        try:
            return await fn()
        except retry_on as exc:  # noqa: PERF203
            last_error = exc
            if attempt >= attempts:
                break
            delay = base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.2)
            await asyncio.sleep(delay)
    assert last_error is not None
    raise last_error
