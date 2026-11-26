"""成员查询与身份绑定接口。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.entities import AppUser, Member, MemberIdentity
from app.schemas.member import IdentityBindIn
from app.services.auth import require_roles

router = APIRouter(prefix="/members", tags=["members"])


@router.get("")
async def list_members(
    _manager: AppUser = Depends(require_roles("admin", "leader")),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    members = (
        await session.scalars(select(Member).order_by(Member.id))
    ).all()
    return [
        {
            "id": member.id,
            "name": member.name,
            "email": member.email,
            "role": member.role,
            "status": member.status,
        }
        for member in members
    ]


@router.post("/{member_id}/identities", status_code=201)
async def bind_identity(
    member_id: int,
    body: IdentityBindIn,
    _manager: AppUser = Depends(require_roles("admin", "leader")),
    session: AsyncSession = Depends(get_session),
) -> dict:
    member = await session.get(Member, member_id)
    if member is None:
        raise HTTPException(status_code=404, detail="成员不存在")

    identity = MemberIdentity(
        member_id=member_id,
        provider=body.provider,
        external_id=body.external_id,
        external_username=body.external_username,
        verified=True,
    )
    session.add(identity)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=409, detail="该外部身份已绑定"
        ) from None

    return {
        "id": identity.id,
        "member_id": identity.member_id,
        "provider": identity.provider,
        "external_id": identity.external_id,
    }
