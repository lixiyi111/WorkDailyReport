"""Mock 数据源：不依赖外部凭证，用于演示与集成测试。"""

from datetime import timedelta

from app.services.collectors.base import (
    CollectionResult,
    RawCommitData,
    RawMessageData,
    RawTaskData,
    TimeWindow,
)


class MockGitHubCollector:
    source = "github"

    def __init__(self, member_emails: list[str] | None = None) -> None:
        self.emails = member_emails or ["alice@example.com", "bob@example.com"]

    async def collect(self, window: TimeWindow) -> CollectionResult[RawCommitData]:
        day = window.start.date().isoformat()
        items = [
            RawCommitData(
                repo_full_name="demo/daily-report",
                sha=f"mock{day}01",
                author_name="Alice",
                author_email=self.emails[0],
                committed_at=window.start + timedelta(hours=9),
                message="feat: 实现日报生成模板",
                branch="main",
                url=f"https://example.com/commit/mock{day}01",
            ),
            RawCommitData(
                repo_full_name="demo/daily-report",
                sha=f"mock{day}02",
                author_name="Bob",
                author_email=self.emails[1 % len(self.emails)],
                committed_at=window.start + timedelta(hours=10),
                message="fix: 修复跨零点归属问题",
                branch="main",
                url=f"https://example.com/commit/mock{day}02",
            ),
        ]
        return CollectionResult(items=items)


class MockFeishuTaskCollector:
    source = "feishu_tasks"

    def __init__(self, member_emails: list[str] | None = None) -> None:
        self.emails = member_emails or ["alice@example.com", "bob@example.com"]

    async def collect(self, window: TimeWindow) -> CollectionResult[RawTaskData]:
        day = window.start.date().isoformat()
        items = [
            RawTaskData(
                task_id=f"task-{day}-01",
                title="完成日报模板设计",
                owner_external_id=self.emails[0],
                owner_name="Alice",
                owner_email=self.emails[0],
                status="done",
                status_changed_at=window.start + timedelta(hours=11),
                created_at_source=window.start + timedelta(hours=8),
            ),
            RawTaskData(
                task_id=f"task-{day}-02",
                title="联调飞书任务接口",
                owner_external_id=self.emails[1 % len(self.emails)],
                owner_name="Bob",
                owner_email=self.emails[1 % len(self.emails)],
                status="in_progress",
                status_changed_at=window.start + timedelta(hours=12),
                created_at_source=window.start + timedelta(hours=8),
            ),
        ]
        return CollectionResult(items=items)


class MockFeishuMessageCollector:
    source = "feishu_messages"

    def __init__(self, member_emails: list[str] | None = None) -> None:
        self.emails = member_emails or ["alice@example.com", "bob@example.com"]

    async def collect(self, window: TimeWindow) -> CollectionResult[RawMessageData]:
        day = window.start.date().isoformat()
        items = [
            RawMessageData(
                message_id=f"msg-{day}-01",
                chat_id="mock-chat",
                sender_external_id=self.emails[0],
                sender_name="Alice",
                sender_email=self.emails[0],
                sent_at=window.start + timedelta(hours=13),
                content="已完成后端接口联调，明天继续前端。",
            ),
            RawMessageData(
                message_id=f"msg-{day}-02",
                chat_id="mock-chat",
                sender_external_id=self.emails[1 % len(self.emails)],
                sender_name="Bob",
                sender_email=self.emails[1 % len(self.emails)],
                sent_at=window.start + timedelta(hours=14),
                content="帮忙 review 了日报汇总的逻辑。",
            ),
        ]
        return CollectionResult(items=items)
