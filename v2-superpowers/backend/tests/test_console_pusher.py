"""V2-032：控制台推送（可断言、不依赖外部服务）。"""

from datetime import date

from app.services.pushers.console import ConsolePusher
from app.services.reports.types import GeneratedReport

REPORT = GeneratedReport(
    report_date=date(2026, 11, 6),
    report_type="team",
    member_id=None,
    member_name="全组",
    content_md="# 团队日报（2026-11-06）\n",
    summary={},
    items=[],
)


async def test_console_push_output() -> None:
    outputs: list[str] = []
    pusher = ConsolePusher(writer=outputs.append)
    result = await pusher.push(REPORT, "console")

    assert result.success is True
    assert result.attempts == 1
    assert outputs == [REPORT.content_md]
