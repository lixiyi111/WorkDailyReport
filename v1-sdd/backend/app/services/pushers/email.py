"""SMTP 邮件推送。"""

import asyncio
import smtplib
from email.message import EmailMessage

from app.services.pushers.base import PushResult


class EmailPusher:
    channel = "email"

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        auth_code: str,
        from_name: str = "智能日报",
    ) -> None:
        self.host = host
        self.port = port
        self.user = user
        self.auth_code = auth_code
        self.from_name = from_name

    async def push(self, subject: str, content: str, target: str) -> PushResult:
        recipients = [t.strip() for t in target.replace(";", ",").split(",") if t.strip()]
        if not self.user or not self.auth_code:
            return PushResult(self.channel, target, False, error="SMTP 未配置")
        if not recipients:
            return PushResult(self.channel, target, False, error="收件人为空")

        last_error: str | None = None
        for attempt in range(1, 4):
            try:
                await asyncio.to_thread(self._send, subject, content, recipients)
                return PushResult(self.channel, target, True, attempt=attempt)
            except Exception as exc:  # noqa: BLE001
                last_error = f"{type(exc).__name__}: {exc}"
                if attempt < 3:
                    await asyncio.sleep(0.5 * 2 ** (attempt - 1))
        return PushResult(self.channel, target, False, attempt=3, error=last_error)

    def _send(self, subject: str, content: str, recipients: list[str]) -> None:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = f"{self.from_name} <{self.user}>"
        message["To"] = ", ".join(recipients)
        message.set_content(content)
        with smtplib.SMTP_SSL(self.host, self.port, timeout=30) as smtp:
            smtp.login(self.user, self.auth_code)
            smtp.send_message(message)
