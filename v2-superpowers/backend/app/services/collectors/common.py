"""采集器共享工具：可恢复错误与时间戳解析。"""

from __future__ import annotations

from datetime import UTC, datetime


class FetchError(Exception):
    """单数据源可恢复错误；由采集器转换为 SourceError。"""

    def __init__(self, code: str, message: str, retryable: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable


def _from_number(value: int | float) -> datetime:
    seconds = float(value)
    if seconds > 10_000_000_000:  # 13 位毫秒时间戳
        seconds /= 1000
    return datetime.fromtimestamp(seconds, tz=UTC).replace(tzinfo=None)


def parse_timestamp(value: object) -> datetime | None:
    """兼容 Feishu 的毫秒数字、数字字符串与 ISO 8601。"""
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return _from_number(value)
    text = str(value)
    if text.isdigit():
        return _from_number(int(text))
    parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC).replace(tzinfo=None)
