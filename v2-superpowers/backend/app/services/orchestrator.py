"""日报编排器：采集 → 持久化 → 身份/归属 → 个人/团队日报 → 推送。

- 同一日期用进程内锁防止重入；
- 原始数据与日报均按自然键 upsert，重跑不产生重复；
- 单数据源失败降级为 partial，不中断整份日报。
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from typing import Protocol

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.contracts import AuthError, CollectionResult, SourceError, TimeWindow
from app.core.timeutil import day_window
from app.models.entities import (
    DailyReport,
    Member,
    MemberIdentity,
    PushLog,
    RawCommit,
    RawMessage,
    RawTask,
    ReportItem,
    ReportVersion,
    Repository,
    SourceSyncState,
    utcnow,
)
from app.services.attribution import AttributedItem, AttributionEngine, RawRecord
from app.services.identity import IdentityResolver
from app.services.pushers.base import PushResult
from app.services.reports.personal import PersonalReportGenerator
from app.services.reports.team import TeamReportGenerator
from app.services.reports.types import GeneratedReport


class CollectorLike(Protocol):
    source: str

    async def collect(self, window: TimeWindow) -> CollectionResult: ...


class PusherLike(Protocol):
    channel: str

    async def push(self, report: GeneratedReport, target: str) -> PushResult: ...


@dataclass
class CollectorSet:
    github: CollectorLike
    tasks: CollectorLike
    messages: CollectorLike


@dataclass(frozen=True)
class RunSummary:
    report_date: date
    personal_reports: int
    team_reports: int
    commits: int
    tasks: int
    messages: int
    items: int
    partial: bool
    errors: list[SourceError] = field(default_factory=list)
    pushed: int = 0


_DATE_LOCKS: dict[date, asyncio.Lock] = {}


def _lock_for(report_date: date) -> asyncio.Lock:
    return _DATE_LOCKS.setdefault(report_date, asyncio.Lock())


def _first_line(text: str) -> str:
    stripped = text.strip()
    return stripped.splitlines()[0] if stripped else "(无提交说明)"


class DailyReportOrchestrator:
    def __init__(
        self,
        session: AsyncSession,
        *,
        collectors: CollectorSet,
        pushers: list[PusherLike],
        email_targets: str = "",
        feishu_chat_id: str | None = None,
    ) -> None:
        self.session = session
        self.collectors = collectors
        self.pushers = pushers
        self.email_targets = email_targets
        self.feishu_chat_id = feishu_chat_id
        self.resolver = IdentityResolver(session)

    async def run(self, report_date: date, push: bool = True) -> RunSummary:
        async with _lock_for(report_date):
            return await self._run(report_date, push)

    async def _run(self, report_date: date, push: bool) -> RunSummary:
        window = day_window(report_date)
        try:
            github, tasks, messages = await self._collect_all(window)
            errors: list[SourceError] = []
            errors.extend(github.errors)
            errors.extend(tasks.errors)
            errors.extend(messages.errors)

            commit_errors, commit_partial = await self._persist_commits(github.items)
            task_errors, task_partial = await self._persist_tasks(tasks.items)
            message_errors, message_partial = await self._persist_messages(messages.items)
            errors.extend(commit_errors)
            errors.extend(task_errors)
            errors.extend(message_errors)

            records = await self._build_records(window)
            attributed: list[AttributedItem] = AttributionEngine().attribute(records)
            personal_reports = await self._generate_personal(
                report_date, attributed
            )
            team_report = TeamReportGenerator().generate(
                report_date=report_date, personal_reports=personal_reports
            )

            for report in personal_reports:
                await self._upsert_report(report)
            team_id = await self._upsert_report(team_report)

            pushed = 0
            if push:
                pushed = await self._push(team_report, team_id)

            await self._update_sync_state(
                "github", report_date.isoformat(), github.partial or commit_partial, errors
            )
            await self._update_sync_state(
                "feishu_tasks",
                report_date.isoformat(),
                tasks.partial or task_partial,
                errors,
            )
            await self._update_sync_state(
                "feishu_messages",
                report_date.isoformat(),
                messages.partial or message_partial,
                errors,
            )
            await self.session.commit()

            return RunSummary(
                report_date=report_date,
                personal_reports=len(personal_reports),
                team_reports=1,
                commits=len(github.items),
                tasks=len(tasks.items),
                messages=len(messages.items),
                items=len(attributed),
                partial=github.partial
                or tasks.partial
                or messages.partial
                or commit_partial
                or task_partial
                or message_partial,
                errors=errors,
                pushed=pushed,
            )
        except Exception:
            await self.session.rollback()
            raise

    async def _collect_all(
        self, window: TimeWindow
    ) -> tuple[CollectionResult, CollectionResult, CollectionResult]:
        raw = await asyncio.gather(
            self.collectors.github.collect(window),
            self.collectors.tasks.collect(window),
            self.collectors.messages.collect(window),
            return_exceptions=True,
        )
        sources = ("github", "feishu_tasks", "feishu_messages")
        normalized: list[CollectionResult] = []
        for source, result in zip(sources, raw, strict=True):
            normalized.append(self._normalize(result, source))
        return normalized[0], normalized[1], normalized[2]

    @staticmethod
    def _normalize(result: object, source: str) -> CollectionResult:
        if isinstance(result, Exception):
            code = "AUTH" if isinstance(result, AuthError) else "INTERNAL"
            return CollectionResult(
                items=[],
                partial=True,
                errors=[
                    SourceError(
                        source=source,
                        code=code,
                        message=str(result),
                        retryable=False,
                    )
                ],
            )
        return result  # type: ignore[return-value]

    async def _persist_commits(
        self, records: list
    ) -> tuple[list[SourceError], bool]:
        repos = (
            await self.session.scalars(
                select(Repository).where(Repository.enabled.is_(True))
            )
        ).all()
        repo_map = {f"{repo.owner}/{repo.name}": repo for repo in repos}
        errors: list[SourceError] = []
        partial = False

        for record in records:
            repo = repo_map.get(record.repo)
            if repo is None:
                errors.append(
                    SourceError(
                        source="github",
                        code="CONFIG",
                        message=f"仓库未配置: {record.repo}",
                    )
                )
                partial = True
                continue

            external_id = record.author_email or record.author_name
            member_id = await self.resolver.resolve(
                "github",
                external_id,
                external_username=record.author_name,
                email=record.author_email,
            )
            identity_id = await self._identity_id("github", external_id)
            if member_id is None:
                await self.resolver.record_unmatched(
                    "github",
                    external_id,
                    record.author_name,
                    "commit",
                    record.sha,
                )

            existing = await self.session.scalar(
                select(RawCommit).where(
                    RawCommit.repo_id == repo.id, RawCommit.sha == record.sha
                )
            )
            if existing is None:
                self.session.add(
                    RawCommit(
                        repo_id=repo.id,
                        sha=record.sha,
                        author_identity_id=identity_id,
                        author_name=record.author_name,
                        author_email=record.author_email,
                        committed_at=record.committed_at,
                        message=record.message,
                        branch=record.branch,
                        url=record.url,
                        pr_number=record.pr_number,
                    )
                )
            else:
                existing.author_identity_id = (
                    identity_id or existing.author_identity_id
                )
                existing.message = record.message
                existing.committed_at = record.committed_at

        await self.session.flush()
        return errors, partial

    async def _persist_tasks(self, records: list) -> tuple[list[SourceError], bool]:
        errors: list[SourceError] = []
        partial = False

        for record in records:
            owner_identity_id = None
            if record.owner_external_id:
                member_id = await self.resolver.resolve(
                    "feishu", record.owner_external_id
                )
                owner_identity_id = await self._identity_id(
                    "feishu", record.owner_external_id
                )
                if member_id is None:
                    await self.resolver.record_unmatched(
                        "feishu",
                        record.owner_external_id,
                        None,
                        "task",
                        record.task_id,
                    )

            for participant in record.participants:
                member_id = await self.resolver.resolve("feishu", participant)
                if member_id is None:
                    await self.resolver.record_unmatched(
                        "feishu", participant, None, "task", record.task_id
                    )

            existing = await self.session.scalar(
                select(RawTask).where(RawTask.task_id == record.task_id)
            )
            if existing is None:
                self.session.add(
                    RawTask(
                        task_id=record.task_id,
                        title=record.title,
                        owner_identity_id=owner_identity_id,
                        participants_json=record.participants,
                        status=record.status,
                        status_changed_at=record.status_changed_at,
                        created_at_source=record.created_at_source,
                        updated_at_source=record.updated_at_source,
                    )
                )
            else:
                existing.title = record.title
                existing.owner_identity_id = (
                    owner_identity_id or existing.owner_identity_id
                )
                existing.participants_json = record.participants
                existing.status = record.status
                existing.status_changed_at = record.status_changed_at

        await self.session.flush()
        return errors, partial

    async def _persist_messages(self, records: list) -> tuple[list[SourceError], bool]:
        errors: list[SourceError] = []
        partial = False

        for record in records:
            sender_identity_id = None
            if record.sender_external_id:
                member_id = await self.resolver.resolve(
                    "feishu",
                    record.sender_external_id,
                    external_username=record.sender_name,
                )
                sender_identity_id = await self._identity_id(
                    "feishu", record.sender_external_id
                )
                if member_id is None:
                    await self.resolver.record_unmatched(
                        "feishu",
                        record.sender_external_id,
                        record.sender_name,
                        "message",
                        record.message_id,
                    )

            existing = await self.session.scalar(
                select(RawMessage).where(
                    RawMessage.message_id == record.message_id
                )
            )
            if existing is None:
                self.session.add(
                    RawMessage(
                        message_id=record.message_id,
                        chat_id=record.chat_id,
                        sender_identity_id=sender_identity_id,
                        sender_name=record.sender_name,
                        sent_at=record.sent_at,
                        content_excerpt=record.content_excerpt,
                        content_hash=record.content_hash,
                    )
                )
            else:
                existing.sender_identity_id = (
                    sender_identity_id or existing.sender_identity_id
                )
                existing.content_excerpt = record.content_excerpt

        await self.session.flush()
        return errors, partial

    async def _identity_id(self, provider: str, external_id: str) -> int | None:
        identity = await self.session.scalar(
            select(MemberIdentity).where(
                MemberIdentity.provider == provider,
                MemberIdentity.external_id == external_id,
            )
        )
        return identity.id if identity is not None else None

    async def _member_for_identity(self, identity_id: int | None) -> int | None:
        if identity_id is None:
            return None
        identity = await self.session.get(MemberIdentity, identity_id)
        return identity.member_id if identity is not None else None

    async def _build_records(self, window: TimeWindow) -> list[RawRecord]:
        records: list[RawRecord] = []

        commits = (
            await self.session.scalars(
                select(RawCommit).where(
                    RawCommit.committed_at >= window.start,
                    RawCommit.committed_at < window.end,
                )
            )
        ).all()
        for commit in commits:
            member_id = await self._member_for_identity(
                commit.author_identity_id
            )
            if member_id is not None:
                records.append(
                    RawRecord(
                        source_type="commit",
                        source_id=commit.sha,
                        title=_first_line(commit.message),
                        member_id=member_id,
                        role="author",
                        detail=commit.message,
                        occurred_at=commit.committed_at,
                    )
                )

        tasks = (
            await self.session.scalars(
                select(RawTask).where(
                    RawTask.status_changed_at >= window.start,
                    RawTask.status_changed_at < window.end,
                )
            )
        ).all()
        for task in tasks:
            owner = await self._member_for_identity(task.owner_identity_id)
            if owner is not None:
                records.append(
                    RawRecord(
                        source_type="task",
                        source_id=task.task_id,
                        title=task.title,
                        member_id=owner,
                        role="owner",
                        occurred_at=task.status_changed_at,
                    )
                )
            for participant in task.participants_json or []:
                identity = await self.session.scalar(
                    select(MemberIdentity).where(
                        MemberIdentity.provider == "feishu",
                        MemberIdentity.external_id == str(participant),
                    )
                )
                if identity is not None:
                    records.append(
                        RawRecord(
                            source_type="task",
                            source_id=task.task_id,
                            title=task.title,
                            member_id=identity.member_id,
                            role="participant",
                            occurred_at=task.status_changed_at,
                        )
                    )

        messages = (
            await self.session.scalars(
                select(RawMessage).where(
                    RawMessage.sent_at >= window.start,
                    RawMessage.sent_at < window.end,
                )
            )
        ).all()
        for message in messages:
            sender = await self._member_for_identity(
                message.sender_identity_id
            )
            if sender is not None:
                records.append(
                    RawRecord(
                        source_type="message",
                        source_id=message.message_id,
                        title=message.content_excerpt or "(无消息摘要)",
                        member_id=sender,
                        role="participant",
                        occurred_at=message.sent_at,
                    )
                )

        return records

    async def _generate_personal(
        self, report_date: date, attributed: list[AttributedItem]
    ) -> list[GeneratedReport]:
        members = (
            await self.session.scalars(
                select(Member)
                .where(Member.status == "active")
                .order_by(Member.id)
            )
        ).all()
        by_member: dict[int, list[AttributedItem]] = defaultdict(list)
        for item in attributed:
            by_member[item.member_id].append(item)

        generator = PersonalReportGenerator()
        return [
            generator.generate(
                member_id=member.id,
                member_name=member.name,
                report_date=report_date,
                items=by_member.get(member.id, []),
            )
            for member in members
        ]

    async def _upsert_report(self, report: GeneratedReport) -> int:
        scope_key = (
            f"member:{report.member_id}"
            if report.report_type == "personal"
            else "team"
        )
        row = await self.session.scalar(
            select(DailyReport).where(
                DailyReport.report_date == report.report_date,
                DailyReport.report_type == report.report_type,
                DailyReport.scope_key == scope_key,
            )
        )
        if row is None:
            row = DailyReport(
                report_date=report.report_date,
                report_type=report.report_type,
                scope_key=scope_key,
                member_id=report.member_id,
                status="generated",
                current_version=1,
                content_md=report.content_md,
                summary_json=report.summary,
            )
            self.session.add(row)
            await self.session.flush()
        else:
            row.member_id = report.member_id
            row.status = "generated"
            row.content_md = report.content_md
            row.summary_json = report.summary
            row.updated_at = utcnow()

        await self.session.execute(
            delete(ReportItem).where(ReportItem.report_id == row.id)
        )
        for order, item in enumerate(report.items):
            self.session.add(
                ReportItem(
                    report_id=row.id,
                    category=item.category,
                    title=item.title,
                    detail=item.detail,
                    source_type=item.source_type,
                    source_id=item.source_id,
                    attribution_role=item.attribution_role,
                    sort_order=order,
                )
            )

        version = await self.session.scalar(
            select(ReportVersion.id).where(
                ReportVersion.report_id == row.id,
                ReportVersion.version == 1,
            )
        )
        if version is None:
            self.session.add(
                ReportVersion(
                    report_id=row.id,
                    version=1,
                    content_md=report.content_md,
                    editor="generator",
                    change_note="自动生成",
                )
            )

        await self.session.flush()
        return row.id

    async def _push(self, report: GeneratedReport, report_id: int) -> int:
        pushed = 0
        for pusher in self.pushers:
            if pusher.channel == "email":
                target = self.email_targets
            elif pusher.channel == "feishu":
                target = self.feishu_chat_id or ""
            else:
                target = "console"
            if pusher.channel in ("email", "feishu") and not target:
                continue

            result = await pusher.push(report, target)
            if result.success and not result.skipped:
                pushed += 1
            for attempt in range(1, result.attempts + 1):
                success = result.success and attempt == result.attempts
                self.session.add(
                    PushLog(
                        report_id=report_id,
                        channel=result.channel,
                        target=result.target,
                        status="success" if success else "failed",
                        attempt=attempt,
                        error_message=None if success else result.error,
                    )
                )
        return pushed

    async def _update_sync_state(
        self,
        source: str,
        resource_key: str,
        partial: bool,
        errors: list[SourceError],
    ) -> None:
        row = await self.session.scalar(
            select(SourceSyncState).where(
                SourceSyncState.source == source,
                SourceSyncState.resource_key == resource_key,
            )
        )
        source_errors = [error for error in errors if error.source == source]
        if row is None:
            row = SourceSyncState(source=source, resource_key=resource_key)
            self.session.add(row)
        row.last_synced_at = utcnow()
        row.status = "partial" if partial else "success"
        row.error_message = (
            "; ".join(error.message for error in source_errors) or None
        )
