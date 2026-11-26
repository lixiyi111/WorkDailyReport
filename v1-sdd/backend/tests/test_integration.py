"""集成测试：SQLite + Mock 采集 + 控制台推送，验证完整链路与幂等。"""

from datetime import date

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import Settings
from app.db.base import Base
from app.models import DailyReport, Member, PushLog
from app.services.collectors import (
    MockFeishuMessageCollector,
    MockFeishuTaskCollector,
    MockGitHubCollector,
)
from app.services.orchestrator import DailyReportOrchestrator
from app.services.pushers import ConsolePusher


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite://", poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as db_session:
        yield db_session
    await engine.dispose()


@pytest.mark.asyncio
async def test_end_to_end_and_idempotent(session) -> None:
    members = [
        Member(name="Alice", email="alice@example.com"),
        Member(name="Bob", email="bob@example.com"),
        Member(name="Carol", email="carol@example.com"),
    ]
    session.add_all(members)
    await session.commit()

    emails = ["alice@example.com", "bob@example.com"]
    collectors = [
        MockGitHubCollector(emails),
        MockFeishuTaskCollector(emails),
        MockFeishuMessageCollector(emails),
    ]
    orchestrator = DailyReportOrchestrator(
        session=session,
        collectors=collectors,
        pushers=[ConsolePusher()],
        settings=Settings(_env_file=None),
    )

    result = await orchestrator.run(date(2026, 11, 25))
    assert result["personal_reports"] == 3
    assert result["items"] > 0
    assert any(push["success"] for push in result["pushes"])

    personal_count = (
        await session.execute(
            select(func.count()).select_from(DailyReport).where(
                DailyReport.report_type == "personal"
            )
        )
    ).scalar_one()
    team_count = (
        await session.execute(
            select(func.count()).select_from(DailyReport).where(
                DailyReport.report_type == "team"
            )
        )
    ).scalar_one()
    assert personal_count == 3
    assert team_count == 1

    carol_report = (
        await session.execute(
            select(DailyReport).where(
                DailyReport.report_type == "personal",
                DailyReport.member_id == members[2].id,
            )
        )
    ).scalar_one()
    assert "无产出" in carol_report.content_md

    # 幂等：重复运行不新增日报
    await orchestrator.run(date(2026, 11, 25))
    personal_count_2 = (
        await session.execute(
            select(func.count()).select_from(DailyReport).where(
                DailyReport.report_type == "personal"
            )
        )
    ).scalar_one()
    team_count_2 = (
        await session.execute(
            select(func.count()).select_from(DailyReport).where(
                DailyReport.report_type == "team"
            )
        )
    ).scalar_one()
    assert personal_count_2 == 3
    assert team_count_2 == 1

    push_count = (
        await session.execute(select(func.count()).select_from(PushLog))
    ).scalar_one()
    assert push_count == 1  # 第二次运行跳过重复推送
