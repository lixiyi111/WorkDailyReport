"""日报主编排：串联采集、持久化、生成与推送。"""

import asyncio
from datetime import date

from sqlalchemy import and_, delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.timeutil import natural_day_window_utc, now_utc
from app.models import (
    AttendanceRecord,
    CollectionRun,
    DailyReport,
    Member,
    MemberIdentity,
    PushLog,
    RawCommit,
    RawMessage,
    RawTask,
    ReportItem,
    Repository,
    SourceSyncState,
)
from app.services.attribution import AttributedItem, AttributionEngine
from app.services.collectors.base import (
    AuthError,
    CollectionResult,
    RawCommitData,
    RawMessageData,
    RawTaskData,
    TimeWindow,
)
from app.services.identity import IdentityResolver
from app.services.pushers.base import Pusher
from app.services.reports.personal import GeneratedReport, PersonalReportGenerator
from app.services.reports.team import TeamReportGenerator

DONE_STATUSES = ("done", "completed", "closed", "finished")
BLOCKED_STATUSES = ("blocked", "blocked_by")

# 进程内运行锁：API 每次请求都会新建 orchestrator，实例级锁无法跨请求生效。
_run_locks: dict[int, asyncio.Lock] = {}


def _get_run_lock() -> asyncio.Lock:
    loop = asyncio.get_running_loop()
    return _run_locks.setdefault(id(loop), asyncio.Lock())


class DailyReportOrchestrator:
    def __init__(
        self,
        session: AsyncSession,
        collectors: list,
        pushers: list[Pusher],
        settings: Settings,
        resolver: IdentityResolver | None = None,
    ) -> None:
        self.session = session
        self.collectors = collectors
        self.pushers = pushers
        self.settings = settings
        self.resolver = resolver or IdentityResolver(session)
        self.attribution = AttributionEngine()
        self.personal_gen = PersonalReportGenerator()
        self.team_gen = TeamReportGenerator()

    async def run(self, report_date: date, push: bool = True) -> dict:
        async with _get_run_lock():
            run = CollectionRun(
                run_type="daily",
                status="running",
                started_at=now_utc(),
                detail_json={"report_date": report_date.isoformat()},
            )
            self.session.add(run)
            await self.session.flush()
            try:
                start, end = natural_day_window_utc(report_date)
                window = TimeWindow(start=start, end=end)
                by_source, errors = await self._collect(window)
                await self._persist(by_source)
                await self._update_sync_state(by_source, errors)
                await self.session.flush()
                items = await self._build_items(start, end)
                personal = await self._generate_personal(report_date, items)
                team_report, team_generated = await self._generate_team(
                    report_date, personal, items
                )
                pushes = await self._push(team_report, team_generated) if push else []
                collected = {
                    source: len(result.items) for source, result in by_source.items()
                }
                run.status = "success" if not errors else "partial"
                run.records_count = sum(collected.values())
                run.finished_at = now_utc()
                run.detail_json = {
                    "report_date": report_date.isoformat(),
                    "collected": collected,
                    "errors": errors,
                    "personal_reports": len(personal),
                    "items": len(items),
                    "pushes": pushes,
                }
                await self.session.commit()
                return {
                    "run_id": run.id,
                    "report_date": report_date.isoformat(),
                    "collected": collected,
                    "errors": errors,
                    "personal_reports": len(personal),
                    "items": len(items),
                    "team_report_id": team_report.id,
                    "pushes": pushes,
                    "push_enabled": push,
                }
            except Exception as exc:
                run.status = "failed"
                run.finished_at = now_utc()
                run.error_message = f"{type(exc).__name__}: {exc}"[:1024]
                await self.session.commit()
                raise

    async def _update_sync_state(self, by_source: dict, errors: list[dict]) -> None:
        error_by_source: dict[str, list[str]] = {}
        for error in errors:
            error_by_source.setdefault(error["source"], []).append(error["message"])
        for source, result in by_source.items():
            row = (
                await self.session.execute(
                    select(SourceSyncState).where(
                        SourceSyncState.source == source,
                        SourceSyncState.resource_key == "default",
                    )
                )
            ).scalar_one_or_none()
            if row is None:
                row = SourceSyncState(source=source, resource_key="default")
                self.session.add(row)
            row.last_synced_at = now_utc()
            source_errors = error_by_source.get(source, [])
            row.status = "partial" if (result.partial or source_errors) else "success"
            row.error_message = "; ".join(source_errors)[:1024] or None

    async def _collect(self, window: TimeWindow) -> tuple[dict, list[dict]]:
        results = await asyncio.gather(
            *(collector.collect(window) for collector in self.collectors),
            return_exceptions=True,
        )
        by_source: dict[str, CollectionResult] = {}
        errors: list[dict] = []
        for collector, result in zip(self.collectors, results, strict=False):
            if isinstance(result, AuthError):
                errors.append({"source": collector.source, "code": "AUTH", "message": str(result)})
                by_source[collector.source] = CollectionResult()
            elif isinstance(result, Exception):
                errors.append(
                    {"source": collector.source, "code": "UNKNOWN", "message": type(result).__name__}
                )
                by_source[collector.source] = CollectionResult()
            else:
                by_source[collector.source] = result
                errors.extend(
                    {"source": error.source, "code": error.code, "message": error.message}
                    for error in result.errors
                )
        return by_source, errors

    async def _persist(self, by_source: dict) -> None:
        await self._persist_commits(by_source.get("github"))
        await self._persist_tasks(by_source.get("feishu_tasks"))
        await self._persist_messages(by_source.get("feishu_messages"))

    async def _persist_commits(self, result: CollectionResult | None) -> None:
        if not result:
            return
        for data in result.items:
            repo = await self._get_or_create_repo(data.repo_full_name)
            resolved = await self.resolver.resolve(
                "github",
                data.author_email or data.author_name,
                external_username=data.author_name,
                email=data.author_email,
                source_type="commit",
                source_id=data.sha,
            )
            row = await self._get_commit(repo.id, data.sha)
            if row is None:
                self.session.add(
                    RawCommit(
                        repo_id=repo.id,
                        sha=data.sha,
                        author_identity_id=resolved.identity_id,
                        author_name=data.author_name,
                        author_email=data.author_email,
                        committed_at=data.committed_at,
                        message=data.message,
                        branch=data.branch,
                        url=data.url,
                        pr_number=data.pr_number,
                    )
                )
            else:
                row.author_identity_id = resolved.identity_id

    async def _persist_tasks(self, result: CollectionResult | None) -> None:
        if not result:
            return
        for data in result.items:
            resolved = await self.resolver.resolve(
                "feishu",
                data.owner_external_id or data.owner_email or "",
                external_username=data.owner_name,
                email=data.owner_email,
                source_type="task",
                source_id=data.task_id,
            )
            row = await self._get_task(data.task_id)
            if row is None:
                self.session.add(
                    RawTask(
                        task_id=data.task_id,
                        title=data.title,
                        owner_identity_id=resolved.identity_id,
                        participants_json=data.participants,
                        status=data.status,
                        status_changed_at=data.status_changed_at,
                        created_at_source=data.created_at_source,
                    )
                )
            else:
                row.owner_identity_id = resolved.identity_id
                row.status = data.status
                row.status_changed_at = data.status_changed_at

    async def _persist_messages(self, result: CollectionResult | None) -> None:
        if not result:
            return
        for data in result.items:
            resolved = await self.resolver.resolve(
                "feishu",
                data.sender_external_id or data.sender_email or "",
                external_username=data.sender_name,
                email=data.sender_email,
                source_type="message",
                source_id=data.message_id,
            )
            row = await self._get_message(data.message_id)
            if row is None:
                self.session.add(
                    RawMessage(
                        message_id=data.message_id,
                        chat_id=data.chat_id,
                        sender_identity_id=resolved.identity_id,
                        sender_name=data.sender_name,
                        sent_at=data.sent_at,
                        content_excerpt=(data.content or "")[:500],
                    )
                )
            else:
                row.sender_identity_id = resolved.identity_id

    async def _get_or_create_repo(self, full_name: str) -> Repository:
        owner, _, name = full_name.partition("/")
        if not name:
            owner, name = full_name, ""
        result = await self.session.execute(
            select(Repository).where(Repository.owner == owner, Repository.name == name)
        )
        repo = result.scalar_one_or_none()
        if repo is None:
            repo = Repository(owner=owner, name=name)
            self.session.add(repo)
            await self.session.flush()
        return repo

    async def _get_commit(self, repo_id: int, sha: str) -> RawCommit | None:
        result = await self.session.execute(
            select(RawCommit).where(RawCommit.repo_id == repo_id, RawCommit.sha == sha)
        )
        return result.scalar_one_or_none()

    async def _get_task(self, task_id: str) -> RawTask | None:
        result = await self.session.execute(select(RawTask).where(RawTask.task_id == task_id))
        return result.scalar_one_or_none()

    async def _get_message(self, message_id: str) -> RawMessage | None:
        result = await self.session.execute(
            select(RawMessage).where(RawMessage.message_id == message_id)
        )
        return result.scalar_one_or_none()

    async def _build_items(self, start, end) -> list[AttributedItem]:
        commit_rows = (
            await self.session.execute(
                select(RawCommit, Repository)
                .join(Repository, RawCommit.repo_id == Repository.id)
                .where(RawCommit.committed_at >= start, RawCommit.committed_at < end)
            )
        ).all()
        task_rows = (
            await self.session.execute(
                select(RawTask).where(
                    or_(
                        and_(RawTask.status_changed_at >= start, RawTask.status_changed_at < end),
                        and_(RawTask.created_at_source >= start, RawTask.created_at_source < end),
                    )
                )
            )
        ).scalars().all()
        message_rows = (
            await self.session.execute(
                select(RawMessage).where(
                    RawMessage.sent_at >= start, RawMessage.sent_at < end
                )
            )
        ).scalars().all()

        identity_ids = {
            row.author_identity_id for row, _ in commit_rows if row.author_identity_id
        } | {row.owner_identity_id for row in task_rows if row.owner_identity_id} | {
            row.sender_identity_id for row in message_rows if row.sender_identity_id
        }
        identity_map: dict[int, int] = {}
        if identity_ids:
            identities = (
                await self.session.execute(
                    select(MemberIdentity).where(MemberIdentity.id.in_(identity_ids))
                )
            ).scalars().all()
            identity_map = {identity.id: identity.member_id for identity in identities}

        commit_entries: list[tuple[int, RawCommitData]] = []
        for commit, repo in commit_rows:
            member_id = identity_map.get(commit.author_identity_id)
            if member_id:
                commit_entries.append(
                    (
                        member_id,
                        RawCommitData(
                            repo_full_name=f"{repo.owner}/{repo.name}",
                            sha=commit.sha,
                            author_name=commit.author_name,
                            author_email=commit.author_email,
                            committed_at=commit.committed_at,
                            message=commit.message,
                            branch=commit.branch,
                            url=commit.url,
                            pr_number=commit.pr_number,
                        ),
                    )
                )

        task_entries: list[tuple[int, RawTaskData]] = []
        for task in task_rows:
            member_id = identity_map.get(task.owner_identity_id)
            if member_id:
                task_entries.append(
                    (
                        member_id,
                        RawTaskData(
                            task_id=task.task_id,
                            title=task.title,
                            owner_external_id=None,
                            owner_name=None,
                            owner_email=None,
                            participants=task.participants_json or [],
                            status=task.status,
                            status_changed_at=task.status_changed_at,
                            created_at_source=task.created_at_source,
                        ),
                    )
                )

        message_entries: list[tuple[int, RawMessageData]] = []
        for message in message_rows:
            member_id = identity_map.get(message.sender_identity_id)
            if member_id:
                message_entries.append(
                    (
                        member_id,
                        RawMessageData(
                            message_id=message.message_id,
                            chat_id=message.chat_id,
                            sender_external_id=None,
                            sender_name=message.sender_name,
                            sender_email=None,
                            sent_at=message.sent_at,
                            content=message.content_excerpt or "",
                        ),
                    )
                )

        items = (
            self.attribution.attribute_commits(commit_entries)
            + self.attribution.attribute_tasks(task_entries)
            + self.attribution.attribute_messages(message_entries)
        )
        return self.attribution.dedupe(items)

    async def _generate_personal(
        self, report_date: date, items: list[AttributedItem]
    ) -> list[tuple[Member, GeneratedReport]]:
        members = (
            await self.session.execute(select(Member).where(Member.status == "active"))
        ).scalars().all()
        results: list[tuple[Member, GeneratedReport]] = []
        for member in members:
            member_items = [item for item in items if item.member_id == member.id]
            open_tasks = await self._open_tasks_for(member.id)
            attendance = await self._attendance_for(member.id, report_date)
            generated = self.personal_gen.generate(
                member, report_date, member_items, open_tasks, attendance
            )
            report = await self._upsert_report(
                report_date, "personal", f"member:{member.id}", member.id, generated
            )
            await self._replace_items(report.id, member_items)
            results.append((member, generated))
        return results

    async def _generate_team(
        self,
        report_date: date,
        personal: list[tuple[Member, GeneratedReport]],
        items: list[AttributedItem],
    ) -> tuple[DailyReport, GeneratedReport]:
        members = {
            member.id: member
            for member in (
                await self.session.execute(select(Member))
            ).scalars().all()
        }
        collaboration = [
            (members[item.member_id], item)
            for item in items
            if item.role in ("reviewer", "participant") and item.member_id in members
        ]

        risks: list[str] = []
        for member, generated in personal:
            if generated.summary.get("no_output"):
                risks.append(f"{member.name} 当天无产出")
        blocked = (
            await self.session.execute(
                select(RawTask).where(RawTask.status.in_(BLOCKED_STATUSES))
            )
        ).scalars().all()
        risks.extend(f"任务阻塞：{task.title}" for task in blocked)

        generated = self.team_gen.generate(report_date, personal, collaboration, risks)
        report = await self._upsert_report(report_date, "team", "team", None, generated)
        await self._replace_items(report.id, items)
        return report, generated

    async def _attendance_for(self, member_id: int, work_date: date) -> dict | None:
        result = await self.session.execute(
            select(AttendanceRecord).where(
                AttendanceRecord.member_id == member_id,
                AttendanceRecord.work_date == work_date,
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return {
            "status": row.status,
            "check_in": row.check_in.strftime("%H:%M") if row.check_in else None,
            "check_out": row.check_out.strftime("%H:%M") if row.check_out else None,
            "late_minutes": row.late_minutes,
            "early_minutes": row.early_minutes,
        }

    async def _open_tasks_for(self, member_id: int) -> list[str]:
        identities = (
            await self.session.execute(
                select(MemberIdentity.id).where(MemberIdentity.member_id == member_id)
            )
        ).scalars().all()
        if not identities:
            return []
        tasks = (
            await self.session.execute(
                select(RawTask).where(
                    RawTask.owner_identity_id.in_(identities),
                    RawTask.status.notin_(DONE_STATUSES),
                )
            )
        ).scalars().all()
        return [task.title for task in tasks]

    async def _upsert_report(
        self,
        report_date: date,
        report_type: str,
        scope_key: str,
        member_id: int | None,
        generated: GeneratedReport,
    ) -> DailyReport:
        result = await self.session.execute(
            select(DailyReport).where(
                DailyReport.report_date == report_date,
                DailyReport.report_type == report_type,
                DailyReport.scope_key == scope_key,
            )
        )
        report = result.scalar_one_or_none()
        if report is None:
            report = DailyReport(
                report_date=report_date,
                report_type=report_type,
                scope_key=scope_key,
                member_id=member_id,
                content_md=generated.content_md,
                summary_json=generated.summary,
            )
            self.session.add(report)
            await self.session.flush()
        else:
            report.content_md = generated.content_md
            report.summary_json = generated.summary
            report.current_version += 1
            report.status = "generated"
        return report

    async def _replace_items(self, report_id: int, items: list[AttributedItem]) -> None:
        await self.session.execute(delete(ReportItem).where(ReportItem.report_id == report_id))
        for item in items:
            self.session.add(
                ReportItem(
                    report_id=report_id,
                    category=item.category,
                    title=item.title,
                    detail=item.detail,
                    source_type=item.source_type,
                    source_id=item.source_id,
                    attribution_role=item.role,
                    sort_order=item.sort_order,
                )
            )

    async def _push(
        self, report: DailyReport, generated: GeneratedReport
    ) -> list[dict]:
        results: list[dict] = []
        for pusher in self.pushers:
            target = self._target_for(pusher)
            if not target:
                continue
            existing = (
                await self.session.execute(
                    select(PushLog).where(
                        PushLog.report_id == report.id,
                        PushLog.channel == pusher.channel,
                        PushLog.target == target,
                        PushLog.status == "success",
                    )
                )
            ).scalars().first()
            if existing:
                results.append(
                    {"channel": pusher.channel, "target": target, "success": True, "skipped": True}
                )
                continue
            result = await pusher.push(generated.title, generated.content_md, target)
            self.session.add(
                PushLog(
                    report_id=report.id,
                    channel=result.channel,
                    target=result.target,
                    status="success" if result.success else "failed",
                    attempt=result.attempt,
                    error_message=result.error,
                )
            )
            results.append(
                {
                    "channel": result.channel,
                    "target": result.target,
                    "success": result.success,
                    "error": result.error,
                }
            )
        return results

    def _target_for(self, pusher: Pusher) -> str | None:
        if pusher.channel == "console":
            return "stdout"
        if pusher.channel == "email":
            return ",".join(self.settings.report_recipient_list) or None
        if pusher.channel == "feishu":
            return self.settings.feishu_report_chat_id or None
        return None
