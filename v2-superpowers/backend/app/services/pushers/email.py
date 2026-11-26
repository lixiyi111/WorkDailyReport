"""邮件推送：SMTP_SSL + 指数退避重试 + 每次尝试回调。"""

from __future__ import annotations

import asyncio
import smtplib
from collections.abc import Callable
from email.message import EmailMessage

from app.services.pushers.base import AttemptHook, PushResult
from app.services.reports.types import GeneratedReport

SendFunc = Callable[[list[str], str, str], None]


class EmailPusher:
    channel = "email"

    def __init__(
        self,
        *,
        host: str,
        user: str,
        auth_code: str,
        port: int = 465,
        from_name: str = "智能日报",
        attempts: int = 3,
        retry_base_delay: float = 1.0,
        send_func: SendFunc | None = None,
        on_attempt: AttemptHook | None = None,
    ) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.auth_code = auth_code
        self.from_name = from_name
        self.attempts = attempts
        self.retry_base_delay = retry_base_delay
        self.send_func = send_func
        self.on_attempt = on_attempt

    async def push(self, report: GeneratedReport, target: str) -> PushResult:
        recipients = [part.strip() for part in target.split(",") if part.strip()]
        if not recipients:
            return PushResult(
                channel=self.channel,
                target=target,
                success=False,
                attempts=0,
                error="no recipients",
            )

        subject = f"智能日报 · {report.report_date.isoformat()}"
        if report.member_name:
            subject += f" · {report.member_name}"
        last_error: str | None = None

        for attempt in range(1, self.attempts + 1):
            try:
                await asyncio.to_thread(
                    self._send, recipients, subject, report.content_md
                )
            except Exception as exc:
                last_error = str(exc)
                await self._notify(attempt, False, last_error)
                if attempt < self.attempts:
                    delay = self.retry_base_delay * (2 ** (attempt - 1))
                    if delay > 0:
                        await asyncio.sleep(delay)
                continue

            await self._notify(attempt, True, None)
            return PushResult(
                channel=self.channel,
                target=target,
                success=True,
                attempts=attempt,
            )

        return PushResult(
            channel=self.channel,
            target=target,
            success=False,
            attempts=self.attempts,
            error=last_error,
        )

    async def _notify(self, attempt: int, success: bool, error: str | None) -> None:
        if self.on_attempt is not None:
            await self.on_attempt(attempt, success, error)

    def _send(self, recipients: list[str], subject: str, body: str) -> None:
        if self.send_func is not None:
            self.send_func(recipients, subject, body)
            return

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = f"{self.from_name} <{self.user}>"
        message["To"] = ", ".join(recipients)
        message.set_content(body)
        with smtplib.SMTP_SSL(self.host, self.port, timeout=30) as server:
            server.login(self.user, self.auth_code)
            server.send_message(message)
