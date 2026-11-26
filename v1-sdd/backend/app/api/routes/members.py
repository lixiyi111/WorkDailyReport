"""成员与身份绑定接口。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timeutil import now_utc
from app.db.session import get_session
from app.models import (
    IdentityUnmatched,
    Member,
    MemberIdentity,
    RawCommit,
    RawMessage,
    RawTask,
)
from app.schemas import IdentityBind, MemberCreate, MemberUpdate
from app.services.auth import require_roles

router = APIRouter(tags=["members"], dependencies=[Depends(require_roles("admin", "leader"))])


def _member_dict(member: Member) -> dict:
    return {
        "id": member.id,
        "name": member.name,
        "email": member.email,
        "role": member.role,
        "status": member.status,
    }


@router.get("/members")
async def list_members(session: AsyncSession = Depends(get_session)) -> list[dict]:
    members = (await session.execute(select(Member).order_by(Member.id))).scalars().all()
    return [_member_dict(member) for member in members]


@router.post("/members", status_code=201)
async def create_member(
    payload: MemberCreate, session: AsyncSession = Depends(get_session)
) -> dict:
    existing = (
        await session.execute(select(Member).where(Member.email == payload.email))
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="邮箱已存在")
    member = Member(name=payload.name, email=payload.email, role=payload.role)
    session.add(member)
    await session.commit()
    await session.refresh(member)
    return _member_dict(member)


@router.put("/members/{member_id}")
async def update_member(
    member_id: int,
    payload: MemberUpdate,
    session: AsyncSession = Depends(get_session),
) -> dict:
    member = await session.get(Member, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="成员不存在")
    if payload.email and payload.email != member.email:
        existing = (
            await session.execute(
                select(Member).where(
                    Member.email == payload.email, Member.id != member_id
                )
            )
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=409, detail="邮箱已存在")
    for field in ("name", "email", "role", "status"):
        value = getattr(payload, field)
        if value is not None:
            setattr(member, field, value)
    await session.commit()
    await session.refresh(member)
    return _member_dict(member)


@router.delete("/members/{member_id}")
async def deactivate_member(
    member_id: int, session: AsyncSession = Depends(get_session)
) -> dict:
    member = await session.get(Member, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="成员不存在")
    member.status = "inactive"
    await session.commit()
    await session.refresh(member)
    return _member_dict(member)


@router.post("/members/{member_id}/identities", status_code=201)
async def bind_identity(
    member_id: int,
    payload: IdentityBind,
    session: AsyncSession = Depends(get_session),
) -> dict:
    member = await session.get(Member, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="成员不存在")
    existing = (
        await session.execute(
            select(MemberIdentity).where(
                MemberIdentity.provider == payload.provider,
                MemberIdentity.external_id == payload.external_id,
            )
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="该身份已绑定")
    identity = MemberIdentity(
        member_id=member_id,
        provider=payload.provider,
        external_id=payload.external_id,
        external_username=payload.external_username,
        verified=payload.verified,
    )
    session.add(identity)
    await session.flush()

    # 回填此前未归属的原始记录：按 unmatched 表里的 source_type/source_id 更新外键。
    unmatched_rows = (
        await session.execute(
            select(IdentityUnmatched).where(
                IdentityUnmatched.provider == payload.provider,
                IdentityUnmatched.external_id == payload.external_id,
                IdentityUnmatched.resolved_member_id.is_(None),
            )
        )
    ).scalars().all()

    for row in unmatched_rows:
        if row.source_type == "commit":
            await session.execute(
                update(RawCommit)
                .where(RawCommit.sha == row.source_id)
                .values(author_identity_id=identity.id)
            )
        elif row.source_type == "task":
            await session.execute(
                update(RawTask)
                .where(RawTask.task_id == row.source_id)
                .values(owner_identity_id=identity.id)
            )
        elif row.source_type == "message":
            await session.execute(
                update(RawMessage)
                .where(RawMessage.message_id == row.source_id)
                .values(sender_identity_id=identity.id)
            )
        row.resolved_member_id = member_id
        row.resolved_at = now_utc()

    await session.commit()
    await session.refresh(identity)
    return {
        "id": identity.id,
        "member_id": identity.member_id,
        "provider": identity.provider,
        "external_id": identity.external_id,
        "verified": identity.verified,
        "resolved_records": len(unmatched_rows),
    }


@router.get("/identities/unmatched")
async def list_unmatched(
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    rows = (
        await session.execute(
            select(IdentityUnmatched).order_by(IdentityUnmatched.id.desc())
        )
    ).scalars().all()
    return [
        {
            "id": row.id,
            "provider": row.provider,
            "external_id": row.external_id,
            "external_name": row.external_name,
            "source_type": row.source_type,
            "source_id": row.source_id,
            "resolved_member_id": row.resolved_member_id,
            "created_at": row.created_at.isoformat(),
        }
        for row in rows
    ]
