"""考勤查询接口。"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.entities import AppUser, Member
from app.models.entities import AttendanceRecord as AttendanceRecordRow
from app.services.auth import get_current_user

router = APIRouter(prefix="/attendance", tags=["attendance"])


@router.get("")
async def list_attendance(
    date_: date | None = Query(None, alias="date"),
    user: AppUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    stmt = (
        select(AttendanceRecordRow, Member.name)
        .join(Member, AttendanceRecordRow.member_id == Member.id)
        .order_by(
            AttendanceRecordRow.attendance_date.desc(),
            AttendanceRecordRow.id,
        )
    )
    if date_ is not None:
        stmt = stmt.where(AttendanceRecordRow.attendance_date == date_)
    if user.role == "member":
        stmt = stmt.where(AttendanceRecordRow.member_id == user.member_id)

    rows = (await session.execute(stmt)).all()
    return [
        {
            "id": row.id,
            "member_id": row.member_id,
            "member_name": member_name,
            "attendance_date": row.attendance_date.isoformat(),
            "status": row.status,
            "check_in_at": row.check_in_at.isoformat()
            if row.check_in_at
            else None,
            "check_out_at": row.check_out_at.isoformat()
            if row.check_out_at
            else None,
            "source": row.source,
            "source_id": row.source_id,
        }
        for row, member_name in rows
    ]
