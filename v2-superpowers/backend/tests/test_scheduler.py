"""V2-041：次日 09:00 定时任务注册。"""

from app.scheduler import create_scheduler


async def _job() -> None:
    return None


def test_scheduler_job_registered() -> None:
    scheduler = create_scheduler(_job)
    job = scheduler.get_job("daily-report")
    assert job is not None
    assert job.trigger.timezone.key == "Asia/Shanghai"
    fields = {field.name: str(field) for field in job.trigger.fields}
    assert fields["hour"] == "9"
    assert fields["minute"] == "0"
