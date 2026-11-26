"""推送结果与逐次留痕回调。"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class PushResult:
    channel: str
    target: str
    success: bool
    attempts: int
    error: str | None = None


AttemptHook = Callable[[int, bool, str | None], Awaitable[None]]
