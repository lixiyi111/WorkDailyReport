"""V2-003：自然日时间窗口（Asia/Shanghai → UTC）。"""

from datetime import date, datetime

from app.core.timeutil import day_window


def test_day_window_cross_midnight() -> None:
    """上海自然日 2026-11-06 对应 UTC 2026-11-05 16:00 至 11-06 16:00。"""
    window = day_window(date(2026, 11, 6))
    assert window.start == datetime(2026, 11, 5, 16, 0)
    assert window.end == datetime(2026, 11, 6, 16, 0)


def test_window_contains_is_half_open() -> None:
    """窗口是 [start, end)，end 那一刻不计入。"""
    window = day_window(date(2026, 11, 6))
    assert window.contains(datetime(2026, 11, 5, 16, 0))
    assert window.contains(datetime(2026, 11, 6, 15, 59, 59))
    assert not window.contains(datetime(2026, 11, 6, 16, 0))
