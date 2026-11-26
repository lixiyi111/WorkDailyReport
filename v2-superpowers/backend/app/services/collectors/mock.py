"""无凭证 Mock 采集器：字段与真实采集器一致，供演示与集成测试。"""

from __future__ import annotations

import hashlib
from datetime import timedelta

from app.core.contracts import CollectionResult, TimeWindow
from app.services.collectors.feishu_messages import FeishuMessageRecord
from app.services.collectors.feishu_tasks import FeishuTaskRecord
from app.services.collectors.github import CommitRecord, RepoSpec


def _local_name(email: str) -> str:
    return email.split("@", 1)[0]


def _sha(*parts: str) -> str:
    return hashlib.sha1(":".join(parts).encode("utf-8")).hexdigest()


def _report_day(window: TimeWindow) -> str:
    return (window.start + timedelta(hours=8)).date().isoformat()


class MockGitHubCollector:
    source = "github"

    def __init__(self, repos: list[RepoSpec], member_emails: list[str]) -> None:
        self.repos = repos
        self.member_emails = member_emails

    async def collect(self, window: TimeWindow) -> CollectionResult[CommitRecord]:
        day = _report_day(window)
        items: list[CommitRecord] = []
        for repo in self.repos:
            for index, email in enumerate(self.member_emails):
                committed_at = window.start + timedelta(hours=2 + index)
                items.append(
                    CommitRecord(
                        repo=f"{repo.owner}/{repo.name}",
                        sha=_sha(day, repo.owner, repo.name, email),
                        author_name=_local_name(email),
                        author_email=email,
                        committed_at=committed_at,
                        message=f"mock: 完成 {day} 的第 {index + 1} 项任务",
                        branch=repo.default_branch,
                    )
                )
        return CollectionResult(items=items)


class MockFeishuTaskCollector:
    source = "feishu_tasks"

    def __init__(self, member_emails: list[str]) -> None:
        self.member_emails = member_emails

    async def collect(self, window: TimeWindow) -> CollectionResult[FeishuTaskRecord]:
        day = _report_day(window)
        items: list[FeishuTaskRecord] = []
        for index, email in enumerate(self.member_emails):
            changed_at = window.start + timedelta(hours=3 + index)
            items.append(
                FeishuTaskRecord(
                    task_id=f"mock-task-{day}-{index}",
                    title=f"mock 任务 {index + 1}",
                    owner_external_id=f"mock-{_local_name(email)}",
                    participants=[],
                    status="done",
                    status_changed_at=changed_at,
                    created_at_source=changed_at - timedelta(hours=2),
                    updated_at_source=changed_at,
                )
            )
        return CollectionResult(items=items)


class MockFeishuMessageCollector:
    source = "feishu_messages"

    def __init__(self, member_emails: list[str], chat_id: str = "oc_mock") -> None:
        self.member_emails = member_emails
        self.chat_id = chat_id

    async def collect(
        self, window: TimeWindow
    ) -> CollectionResult[FeishuMessageRecord]:
        day = _report_day(window)
        items: list[FeishuMessageRecord] = []
        for index, email in enumerate(self.member_emails):
            sent_at = window.start + timedelta(hours=4 + index)
            excerpt = f"mock 消息 {index + 1}：今天完成了接口联调"
            items.append(
                FeishuMessageRecord(
                    message_id=f"mock-msg-{day}-{index}",
                    chat_id=self.chat_id,
                    sender_external_id=f"mock-{_local_name(email)}",
                    sender_name=_local_name(email),
                    sent_at=sent_at,
                    content_excerpt=excerpt,
                    content_hash=hashlib.sha256(excerpt.encode("utf-8")).hexdigest(),
                )
            )
        return CollectionResult(items=items)
