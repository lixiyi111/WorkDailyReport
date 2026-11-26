"""边界场景测试：时间窗口、数据源降级、未归属身份。"""

from datetime import date, datetime, timedelta

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import Settings
from app.core.timeutil import natural_day_window_utc
from app.db.base import Base
from app.models import DailyReport, IdentityUnmatched, Member
from app.services.collectors.base import CollectionResult, RawCommitData, SourceError
from app.services.orchestrator import DailyReportOrchestrator
from app.services.pushers import ConsolePusher


class DegradedCollector:
    source = "github"

    async def collect(self, window):
        return CollectionResult(
            items=[
                RawCommitData(
                    repo_full_name="demo/repo",
                    sha="unknown1",
                    author_name="Unknown",
                    author_email="unknown@example.com",
                    committed_at=window.start + timedelta(hours=9),
                    message="feat: 未归属的提交",
                )
            ],
            partial=True,
            errors=[SourceError("github", "RATE_LIMIT", "limited", True)],
        )


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db_session:
        yield db_session
    await engine.dispose()


def test_natural_day_window() -> None:
    start, end = natural_day_window_utc(date(2026, 11, 25))
    assert start == datetime(2026, 11, 24, 16, 0)
    assert end == datetime(2026, 11, 25, 16, 0)


@pytest.mark.asyncio
async def test_degraded_source_and_unmatched_identity(session) -> None:
    session.add(Member(name="Alice", email="alice@example.com"))
    await session.commit()

    orchestrator = DailyReportOrchestrator(
        session=session,
        collectors=[DegradedCollector()],
        pushers=[ConsolePusher()],
        settings=Settings(_env_file=None),
    )
    result = await orchestrator.run(date(2026, 11, 25))

    assert result["errors"]
    assert result["personal_reports"] == 1

    alice_report = (
        await session.execute(select(DailyReport).where(DailyReport.report_type == "personal"))
    ).scalar_one()
    assert "无产出" in alice_report.content_md

    unmatched_count = (
        await session.execute(select(func.count()).select_from(IdentityUnmatched))
    ).scalar_one()
    assert unmatched_count == 1
