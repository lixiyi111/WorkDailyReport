"""时间窗口工具：统一按 Asia/Shanghai 计算自然日，再转 UTC 存储。"""

from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

DEFAULT_TZ = "Asia/Shanghai"


def natural_day_window_utc(day: date, tz: str = DEFAULT_TZ) -> tuple[datetime, datetime]:
    """返回某自然日在 UTC 下的半开区间 [start, end)，均为 naive UTC。"""
    zone = ZoneInfo(tz)
    start_local = datetime.combine(day, time.min, tzinfo=zone)
    end_local = start_local + timedelta(days=1)
    start_utc = start_local.astimezone(UTC).replace(tzinfo=None)
    end_utc = end_local.astimezone(UTC).replace(tzinfo=None)
    return start_utc, end_utc


def now_utc() -> datetime:
    """当前 UTC 时间（naive），与数据库存储口径一致。"""
    return datetime.now(UTC).replace(tzinfo=None)
