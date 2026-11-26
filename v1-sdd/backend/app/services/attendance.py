"""考勤数据：当前用 Mock，真实飞书考勤接入后替换采集器。"""

from datetime import date, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AttendanceRecord, Member

STATUS_PATTERN = ["normal", "normal", "normal", "late", "leave", "normal"]


async def collect_mock_attendance(session: AsyncSession, work_date: date) -> int:
    members = (
        await session.execute(select(Member).where(Member.status == "active"))
    ).scalars().all()
    count = 0
    for member in members:
        status = STATUS_PATTERN[(member.id + work_date.day) % len(STATUS_PATTERN)]
        late_minutes = 12 if status == "late" else 0
        check_in = None
        check_out = None
        if status != "leave":
            check_in = datetime(
                work_date.year, work_date.month, work_date.day, 1, 0
            ) + timedelta(minutes=late_minutes)
            check_out = datetime(work_date.year, work_date.month, work_date.day, 10, 5)

        row = (
            await session.execute(
                select(AttendanceRecord).where(
                    AttendanceRecord.member_id == member.id,
                    AttendanceRecord.work_date == work_date,
                )
            )
        ).scalar_one_or_none()
        if row is None:
            row = AttendanceRecord(member_id=member.id, work_date=work_date)
            session.add(row)
        row.check_in = check_in
        row.check_out = check_out
        row.status = status
        row.late_minutes = late_minutes
        row.early_minutes = 0
        row.source = "mock"
        row.raw_json = {"mock": True}
        count += 1
    await session.commit()
    return count


async def list_attendance(
    session: AsyncSession,
    *,
    work_date: date | None = None,
    member_id: int | None = None,
) -> list[dict]:
    stmt = select(AttendanceRecord)
    if work_date:
        stmt = stmt.where(AttendanceRecord.work_date == work_date)
    if member_id:
        stmt = stmt.where(AttendanceRecord.member_id == member_id)
    rows = (await session.execute(stmt.order_by(AttendanceRecord.work_date.desc()))).scalars().all()

    member_ids = {row.member_id for row in rows}
    names: dict[int, str] = {}
    if member_ids:
        members = (
            await session.execute(select(Member).where(Member.id.in_(member_ids)))
        ).scalars().all()
        names = {member.id: member.name for member in members}

    return [
        {
            "id": row.id,
            "member_id": row.member_id,
            "member_name": names.get(row.member_id),
            "work_date": row.work_date.isoformat(),
            "check_in": row.check_in.isoformat() if row.check_in else None,
            "check_out": row.check_out.isoformat() if row.check_out else None,
            "status": row.status,
            "late_minutes": row.late_minutes,
            "early_minutes": row.early_minutes,
            "source": row.source,
        }
        for row in rows
    ]
