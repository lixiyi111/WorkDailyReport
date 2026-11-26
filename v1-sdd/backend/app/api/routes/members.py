"""成员与身份绑定接口。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models import IdentityUnmatched, Member, MemberIdentity
from app.schemas import IdentityBind, MemberCreate

router = APIRouter(tags=["members"])


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
    await session.commit()
    await session.refresh(identity)
    return {
        "id": identity.id,
        "member_id": identity.member_id,
        "provider": identity.provider,
        "external_id": identity.external_id,
        "verified": identity.verified,
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
