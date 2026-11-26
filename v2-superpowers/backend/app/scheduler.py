"""进程内定时调度：次日 09:00（Asia/Shanghai）触发前一自然日任务。"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

JobFunc = Callable[[], Awaitable[None]]


def create_scheduler(
    job: JobFunc,
    *,
    hour: int = 9,
    minute: int = 0,
    tz: str = "Asia/Shanghai",
) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=tz)
    scheduler.add_job(
        job,
        CronTrigger(hour=hour, minute=minute, timezone=tz),
        id="daily-report",
        replace_existing=True,
    )
    return scheduler
