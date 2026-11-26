"""V2-013：无凭证 Mock 采集器。"""

from datetime import date

from app.core.timeutil import day_window
from app.services.collectors.github import RepoSpec
from app.services.collectors.mock import (
    MockFeishuMessageCollector,
    MockFeishuTaskCollector,
    MockGitHubCollector,
)

WINDOW = day_window(date(2026, 11, 6))
EMAILS = ["wang@example.com", "li@example.com"]


async def test_mock_github_collect_without_credentials() -> None:
    collector = MockGitHubCollector(
        repos=[RepoSpec("lixiyi111", "WorkDailyReport")], member_emails=EMAILS
    )
    result = await collector.collect(WINDOW)

    assert result.partial is False
    assert len(result.items) == 2
    assert len({item.sha for item in result.items}) == 2
    assert all(WINDOW.contains(item.committed_at) for item in result.items)


async def test_mock_task_collect() -> None:
    collector = MockFeishuTaskCollector(member_emails=EMAILS)
    result = await collector.collect(WINDOW)

    assert len(result.items) == 2
    assert all(item.owner_external_id for item in result.items)
    assert all(item.status_changed_at is not None for item in result.items)


async def test_mock_message_collect() -> None:
    collector = MockFeishuMessageCollector(member_emails=EMAILS, chat_id="oc_mock")
    result = await collector.collect(WINDOW)

    assert len(result.items) == 2
    assert all(item.chat_id == "oc_mock" for item in result.items)
    assert all(item.content_excerpt for item in result.items)
