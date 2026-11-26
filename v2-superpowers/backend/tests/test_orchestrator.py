"""V2-040：编排器端到端、重跑幂等与单源降级。"""

from datetime import date

from sqlalchemy import func, select

from app.core.contracts import CollectionResult, SourceError
from app.models.entities import (
    AttendanceRecord as AttendanceRecordRow,
)
from app.models.entities import (
    DailyReport,
    Member,
    MemberIdentity,
    RawCommit,
    ReportItem,
    Repository,
)
from app.services.collectors.attendance import MockAttendanceCollector
from app.services.collectors.github import RepoSpec
from app.services.collectors.mock import (
    MockFeishuMessageCollector,
    MockFeishuTaskCollector,
    MockGitHubCollector,
)
from app.services.orchestrator import CollectorSet, DailyReportOrchestrator
from app.services.pushers.console import ConsolePusher

REPORT_DATE = date(2026, 11, 6)
EMAILS = ["wang@example.com", "li@example.com"]


async def _seed(session) -> None:
    members = [
        Member(name="王芳", email=EMAILS[0]),
        Member(name="李四", email=EMAILS[1]),
    ]
    session.add_all(members)
    await session.flush()
    session.add(Repository(owner="lixiyi111", name="WorkDailyReport"))
    for member, email in zip(members, EMAILS, strict=True):
        session.add(
            MemberIdentity(
                member_id=member.id,
                provider="feishu",
                external_id=f"mock-{email.split('@')[0]}",
                external_username=member.name,
                verified=True,
            )
        )
    await session.flush()


def _collectors() -> CollectorSet:
    repos = [RepoSpec("lixiyi111", "WorkDailyReport")]
    return CollectorSet(
        github=MockGitHubCollector(repos, EMAILS),
        tasks=MockFeishuTaskCollector(EMAILS),
        messages=MockFeishuMessageCollector(EMAILS),
        attendance=MockAttendanceCollector(EMAILS),
    )


async def test_orchestrator_end_to_end(session) -> None:
    await _seed(session)
    outputs: list[str] = []
    orchestrator = DailyReportOrchestrator(
        session,
        collectors=_collectors(),
        pushers=[ConsolePusher(writer=outputs.append)],
    )

    summary = await orchestrator.run(REPORT_DATE, push=True)

    assert summary.personal_reports == 2
    assert summary.team_reports == 1
    assert summary.commits == 2
    assert summary.attendance == 2
    assert summary.partial is False
    assert outputs and "团队日报" in outputs[0]

    attendance = await session.scalar(
        select(func.count()).select_from(AttendanceRecordRow)
    )
    assert attendance == 2

    report_count = await session.scalar(select(func.count()).select_from(DailyReport))
    assert report_count == 3
    team = await session.scalar(
        select(DailyReport).where(DailyReport.report_type == "team")
    )
    assert team is not None
    assert "王芳" in team.content_md
    assert "李四" in team.content_md


async def test_orchestrator_rerun_idempotent(session) -> None:
    await _seed(session)
    orchestrator = DailyReportOrchestrator(
        session, collectors=_collectors(), pushers=[]
    )

    first = await orchestrator.run(REPORT_DATE, push=False)
    commits_first = await session.scalar(select(func.count()).select_from(RawCommit))
    reports_first = await session.scalar(select(func.count()).select_from(DailyReport))
    items_first = await session.scalar(select(func.count()).select_from(ReportItem))
    attendance_first = await session.scalar(
        select(func.count()).select_from(AttendanceRecordRow)
    )

    second = await orchestrator.run(REPORT_DATE, push=False)
    commits_second = await session.scalar(select(func.count()).select_from(RawCommit))
    reports_second = await session.scalar(select(func.count()).select_from(DailyReport))
    items_second = await session.scalar(select(func.count()).select_from(ReportItem))
    attendance_second = await session.scalar(
        select(func.count()).select_from(AttendanceRecordRow)
    )

    assert first.personal_reports == second.personal_reports == 2
    assert commits_first == commits_second == 2
    assert reports_first == reports_second == 3
    assert items_first == items_second
    assert attendance_first == attendance_second == 2


class _PartialGitHubCollector:
    source = "github"

    async def collect(self, window) -> CollectionResult:
        return CollectionResult(
            items=[],
            partial=True,
            errors=[
                SourceError(
                    source="github",
                    code="RATE_LIMIT",
                    message="limited",
                    retryable=True,
                )
            ],
        )


async def test_orchestrator_partial_source(session) -> None:
    await _seed(session)
    collectors = _collectors()
    collectors.github = _PartialGitHubCollector()
    orchestrator = DailyReportOrchestrator(
        session, collectors=collectors, pushers=[]
    )

    summary = await orchestrator.run(REPORT_DATE, push=False)

    assert summary.partial is True
    assert summary.personal_reports == 2
    assert summary.team_reports == 1
    assert summary.errors
    reports = await session.scalar(select(func.count()).select_from(DailyReport))
    assert reports == 3
