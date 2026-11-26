"""统一工作记录：把 commit / task / message 归一为同一结构。"""

from datetime import date, datetime
from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timeutil import natural_day_window_utc
from app.models import Member, MemberIdentity, RawCommit, RawMessage, RawTask, Repository


def _window(
    date_from: date | None, date_to: date | None
) -> tuple[datetime | None, datetime | None]:
    start = natural_day_window_utc(date_from)[0] if date_from else None
    end = natural_day_window_utc(date_to)[1] if date_to else None
    return start, end


async def list_work_records(
    session: AsyncSession,
    *,
    record_type: str | None = None,
    source: str | None = None,
    member_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    query: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> dict:
    start, end = _window(date_from, date_to)
    member_identity_ids: set[int] = set()
    if member_id:
        member_identity_ids = set(
            (
                await session.execute(
                    select(MemberIdentity.id).where(MemberIdentity.member_id == member_id)
                )
            ).scalars().all()
        )

    rows: list[dict[str, Any]] = []
    identity_ids: set[int] = set()

    if record_type in (None, "commit") and source in (None, "github"):
        stmt = select(RawCommit, Repository).join(
            Repository, RawCommit.repo_id == Repository.id
        )
        if start:
            stmt = stmt.where(RawCommit.committed_at >= start)
        if end:
            stmt = stmt.where(RawCommit.committed_at < end)
        for commit, repo in (await session.execute(stmt)).all():
            if member_id and commit.author_identity_id not in member_identity_ids:
                continue
            if commit.author_identity_id:
                identity_ids.add(commit.author_identity_id)
            rows.append(
                {
                    "_identity_id": commit.author_identity_id,
                    "id": f"commit:{commit.id}",
                    "record_type": "commit",
                    "source": "github",
                    "title": (commit.message.splitlines() or ["(无提交说明)"])[0][:200],
                    "detail": f"{repo.owner}/{repo.name}@{commit.sha[:7]}",
                    "occurred_at": commit.committed_at.isoformat(),
                    "external_id": commit.sha,
                    "url": commit.url,
                    "extra": {
                        "repo": f"{repo.owner}/{repo.name}",
                        "branch": commit.branch,
                        "author_email": commit.author_email,
                    },
                }
            )

    if record_type in (None, "task") and source in (None, "feishu"):
        stmt = select(RawTask)
        conditions = []
        if start:
            conditions.append(
                or_(
                    and_(RawTask.status_changed_at >= start, RawTask.status_changed_at < end),
                    and_(RawTask.created_at_source >= start, RawTask.created_at_source < end),
                )
            )
        if conditions:
            stmt = stmt.where(*conditions)
        for task in (await session.execute(stmt)).scalars().all():
            if member_id and task.owner_identity_id not in member_identity_ids:
                continue
            if task.owner_identity_id:
                identity_ids.add(task.owner_identity_id)
            occurred = task.status_changed_at or task.created_at_source or task.collected_at
            rows.append(
                {
                    "_identity_id": task.owner_identity_id,
                    "id": f"task:{task.id}",
                    "record_type": "task",
                    "source": "feishu",
                    "title": task.title,
                    "detail": f"状态：{task.status}",
                    "occurred_at": occurred.isoformat() if occurred else None,
                    "external_id": task.task_id,
                    "url": None,
                    "extra": {
                        "status": task.status,
                        "participants": task.participants_json or [],
                    },
                }
            )

    if record_type in (None, "message") and source in (None, "feishu"):
        stmt = select(RawMessage)
        if start:
            stmt = stmt.where(RawMessage.sent_at >= start)
        if end:
            stmt = stmt.where(RawMessage.sent_at < end)
        for message in (await session.execute(stmt)).scalars().all():
            if member_id and message.sender_identity_id not in member_identity_ids:
                continue
            if message.sender_identity_id:
                identity_ids.add(message.sender_identity_id)
            rows.append(
                {
                    "_identity_id": message.sender_identity_id,
                    "id": f"message:{message.id}",
                    "record_type": "message",
                    "source": "feishu",
                    "title": "群消息",
                    "detail": message.content_excerpt or "",
                    "occurred_at": message.sent_at.isoformat(),
                    "external_id": message.message_id,
                    "url": None,
                    "extra": {"chat_id": message.chat_id},
                }
            )

    identity_map: dict[int, int] = {}
    name_map: dict[int, str] = {}
    if identity_ids:
        identities = (
            await session.execute(
                select(MemberIdentity).where(MemberIdentity.id.in_(identity_ids))
            )
        ).scalars().all()
        identity_map = {identity.id: identity.member_id for identity in identities}
        member_ids = {identity.member_id for identity in identities}
        if member_ids:
            members = (
                await session.execute(select(Member).where(Member.id.in_(member_ids)))
            ).scalars().all()
            name_map = {member.id: member.name for member in members}

    result: list[dict[str, Any]] = []
    for row in rows:
        resolved_member_id = identity_map.get(row.pop("_identity_id") or 0)
        row["member_id"] = resolved_member_id
        row["member_name"] = name_map.get(resolved_member_id) if resolved_member_id else None
        if query:
            haystack = f"{row['title']} {row['detail']}".lower()
            if query.lower() not in haystack:
                continue
        result.append(row)

    result.sort(key=lambda item: item["occurred_at"] or "", reverse=True)
    total = len(result)
    return {"items": result[offset : offset + limit], "total": total}
