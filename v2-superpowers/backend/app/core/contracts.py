"""跨层共享的契约：时间窗口、采集结果、错误。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class TimeWindow:
    """半开时间窗口 [start, end)，边界为 UTC naive。"""

    start: datetime
    end: datetime
    tz: str = "Asia/Shanghai"

    def contains(self, value: datetime) -> bool:
        return self.start <= value < self.end


@dataclass
class SourceError:
    """单个数据源的可恢复错误，不中断整份日报。"""

    source: str
    code: str  # AUTH / RATE_LIMIT / NETWORK / PARSE
    message: str
    retryable: bool = False


@dataclass
class CollectionResult[T]:
    """采集结果：允许部分成功。"""

    items: list[T]
    partial: bool = False
    errors: list[SourceError] = field(default_factory=list)
    cursor: str | None = None


class AuthError(RuntimeError):
    """凭证完全缺失或无效；与单源降级不同，需显式抛出。"""
