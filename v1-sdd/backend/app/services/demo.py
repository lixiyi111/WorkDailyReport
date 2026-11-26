"""演示数据：不依赖任何外部凭证，跑通完整链路。"""

from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import DailyReport, Member
from app.services.collectors import (
    MockFeishuMessageCollector,
    MockFeishuTaskCollector,
    MockGitHubCollector,
)
from app.services.orchestrator import DailyReportOrchestrator
from app.services.pushers import ConsolePusher

DEMO_MEMBERS = (
    ("Alice", "alice@example.com"),
    ("Bob", "bob@example.com"),
    ("Carol", "carol@example.com"),
)


async def ensure_demo_members(session: AsyncSession) -> list[Member]:
    members: list[Member] = []
    for name, email in DEMO_MEMBERS:
        result = await session.execute(select(Member).where(Member.email == email))
        member = result.scalar_one_or_none()
        if member is None:
            member = Member(name=name, email=email)
            session.add(member)
            await session.flush()
        members.append(member)
    return members


async def run_demo(
    session: AsyncSession, report_date: date
) -> tuple[dict, DailyReport | None]:
    members = await ensure_demo_members(session)
    emails = [member.email for member in members]
    collectors = [
        MockGitHubCollector(emails),
        MockFeishuTaskCollector(emails),
        MockFeishuMessageCollector(emails),
    ]
    orchestrator = DailyReportOrchestrator(
        session=session,
        collectors=collectors,
        pushers=[ConsolePusher()],
        settings=get_settings(),
    )
    result = await orchestrator.run(report_date)
    team = (
        await session.execute(
            select(DailyReport).where(
                DailyReport.report_date == report_date,
                DailyReport.report_type == "team",
            )
        )
    ).scalar_one_or_none()
    return result, team
