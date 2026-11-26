"""时间窗口：按指定时区的自然日计算，再转换为 UTC naive。"""

from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from app.core.contracts import TimeWindow


def day_window(report_date: date, tz: str = "Asia/Shanghai") -> TimeWindow:
    """返回 report_date 当天的半开窗口，边界为 UTC naive。"""
    zone = ZoneInfo(tz)
    local_start = datetime.combine(report_date, time.min, tzinfo=zone)
    local_end = local_start + timedelta(days=1)
    start = local_start.astimezone(UTC).replace(tzinfo=None)
    end = local_end.astimezone(UTC).replace(tzinfo=None)
    return TimeWindow(start=start, end=end, tz=tz)
