"""未归属身份查询接口。"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.entities import IdentityUnmatched

router = APIRouter(prefix="/identities", tags=["identities"])


@router.get("/unmatched")
async def list_unmatched(
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    rows = (
        await session.scalars(
            select(IdentityUnmatched).order_by(IdentityUnmatched.id)
        )
    ).all()
    return [
        {
            "id": row.id,
            "provider": row.provider,
            "external_id": row.external_id,
            "external_name": row.external_name,
            "source_type": row.source_type,
            "source_id": row.source_id,
            "resolved_member_id": row.resolved_member_id,
        }
        for row in rows
    ]
