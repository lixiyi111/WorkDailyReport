"""控制台推送：把日报打印到标准输出，便于本地演示与测试断言。"""

from __future__ import annotations

from collections.abc import Callable

from app.services.pushers.base import PushResult
from app.services.reports.types import GeneratedReport


class ConsolePusher:
    channel = "console"

    def __init__(self, writer: Callable[[str], None] | None = None) -> None:
        self.writer = writer or print

    async def push(self, report: GeneratedReport, target: str) -> PushResult:
        self.writer(report.content_md)
        return PushResult(
            channel=self.channel,
            target=target,
            success=True,
            attempts=1,
        )
