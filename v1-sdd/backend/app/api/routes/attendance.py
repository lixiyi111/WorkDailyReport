"""考勤接口（当前为 Mock 数据）。"""

from datetime import date

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.services.attendance import collect_mock_attendance, list_attendance
from app.services.auth import get_current_user, require_roles

router = APIRouter(tags=["attendance"], dependencies=[Depends(get_current_user)])


class AttendanceCollect(BaseModel):
    work_date: date


@router.get("/attendance")
async def read_attendance(
    work_date: date | None = Query(None, alias="date"),
    member_id: int | None = None,
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    return await list_attendance(session, work_date=work_date, member_id=member_id)


@router.post(
    "/attendance/collect", dependencies=[Depends(require_roles("admin", "leader"))]
)
async def collect_attendance(
    payload: AttendanceCollect,
    session: AsyncSession = Depends(get_session),
) -> dict:
    count = await collect_mock_attendance(session, payload.work_date)
    return {"work_date": payload.work_date.isoformat(), "collected": count}
