"""V2-003：异步重试工具。"""

import pytest

from app.core.retry import retry_async


async def test_retry_until_success() -> None:
    """前两次失败、第三次成功，总尝试次数为 3。"""
    attempts = 0

    async def operation() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise RuntimeError("temporary")
        return "ok"

    assert await retry_async(operation, attempts=3, base_delay=0) == "ok"
    assert attempts == 3


async def test_retry_exhausted_raises_last_error() -> None:
    """达到上限后抛出最后一次异常。"""

    async def operation() -> str:
        raise RuntimeError("always")

    with pytest.raises(RuntimeError, match="always"):
        await retry_async(operation, attempts=2, base_delay=0)
