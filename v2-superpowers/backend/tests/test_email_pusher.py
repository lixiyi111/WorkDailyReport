"""V2-030：邮件推送（重试、逐次留痕、收件人校验）。"""

from datetime import date

from app.services.pushers.email import EmailPusher
from app.services.reports.types import GeneratedReport

REPORT = GeneratedReport(
    report_date=date(2026, 11, 6),
    report_type="team",
    member_id=None,
    member_name="全组",
    content_md="# 团队日报\n\n## 团队概览\n- 成员：2 人\n",
    summary={"members": 2},
    items=[],
)


async def test_email_push_writes_log() -> None:
    attempts = 0
    logs: list[tuple[int, bool]] = []

    def fake_send(recipients: list[str], subject: str, body: str) -> None:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise RuntimeError("smtp busy")

    async def on_attempt(attempt: int, success: bool, error: str | None) -> None:
        logs.append((attempt, success))

    pusher = EmailPusher(
        host="smtp.example.com",
        user="sender@example.com",
        auth_code="secret",
        send_func=fake_send,
        on_attempt=on_attempt,
        retry_base_delay=0,
    )
    result = await pusher.push(REPORT, "a@example.com,b@example.com")

    assert result.success is True
    assert result.attempts == 3
    assert result.target == "a@example.com,b@example.com"
    assert logs == [(1, False), (2, False), (3, True)]


async def test_email_retry_on_failure() -> None:
    def fake_send(recipients: list[str], subject: str, body: str) -> None:
        raise RuntimeError("smtp down")

    pusher = EmailPusher(
        host="smtp.example.com",
        user="sender@example.com",
        auth_code="secret",
        send_func=fake_send,
        retry_base_delay=0,
    )
    result = await pusher.push(REPORT, "a@example.com")

    assert result.success is False
    assert result.attempts == 3
    assert result.error == "smtp down"


async def test_email_without_recipients() -> None:
    pusher = EmailPusher(
        host="smtp.example.com",
        user="sender@example.com",
        auth_code="secret",
        retry_base_delay=0,
    )
    result = await pusher.push(REPORT, " , ")
    assert result.success is False
    assert result.attempts == 0
    assert result.error == "no recipients"
