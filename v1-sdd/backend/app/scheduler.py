"""定时调度：次日 09:00 生成前一自然日日报（v1 单 worker）。"""

from datetime import date, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import get_settings

_scheduler: AsyncIOScheduler | None = None


async def run_daily_job() -> None:
    from app.db.session import get_session_factory
    from app.services.factory import build_orchestrator

    settings = get_settings()
    report_date = date.today() - timedelta(days=1)
    async with get_session_factory()() as session:
        orchestrator = build_orchestrator(session, settings)
        await orchestrator.run(report_date)


def start_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        return
    hour, minute = (int(part) for part in get_settings().report_push_time.split(":"))
    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_daily_job, "cron", hour=hour, minute=minute, id="daily_report")
    scheduler.start()
    _scheduler = scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
