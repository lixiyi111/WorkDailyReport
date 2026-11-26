"""工作台汇总。"""

from collections import Counter
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.timeutil import natural_day_window_utc
from app.db.session import get_session
from app.models import (
    AttendanceRecord,
    CollectionRun,
    DailyReport,
    DataSource,
    Member,
    RawCommit,
    RawMessage,
    RawTask,
)

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
async def dashboard(
    report_date: date | None = Query(None, alias="date"),
    session: AsyncSession = Depends(get_session),
) -> dict:
    settings = get_settings()
    day = report_date or date.today()
    start, end = natural_day_window_utc(day)

    commits = (
        await session.execute(
            select(func.count())
            .select_from(RawCommit)
            .where(RawCommit.committed_at >= start, RawCommit.committed_at < end)
        )
    ).scalar_one()
    messages = (
        await session.execute(
            select(func.count())
            .select_from(RawMessage)
            .where(RawMessage.sent_at >= start, RawMessage.sent_at < end)
        )
    ).scalar_one()
    tasks = (
        await session.execute(
            select(RawTask).where(
                or_(
                    and_(
                        RawTask.status_changed_at >= start,
                        RawTask.status_changed_at < end,
                    ),
                    and_(
                        RawTask.created_at_source >= start,
                        RawTask.created_at_source < end,
                    ),
                )
            )
        )
    ).scalars().all()
    task_status = Counter(task.status for task in tasks)

    reports = (
        await session.execute(
            select(DailyReport).where(DailyReport.report_date == day)
        )
    ).scalars().all()
    personal = [report for report in reports if report.report_type == "personal"]
    team = [report for report in reports if report.report_type == "team"]
    personal_status = Counter(report.status for report in personal)

    recent_reports = (
        await session.execute(
            select(DailyReport)
            .order_by(DailyReport.report_date.desc(), DailyReport.id.desc())
            .limit(5)
        )
    ).scalars().all()
    members = {
        member.id: member.name
        for member in (await session.execute(select(Member))).scalars().all()
    }

    source_rows = {
        row.source: row
        for row in (await session.execute(select(DataSource))).scalars().all()
    }
    source_defs = [
        ("github", "GitHub", bool(settings.github_token)),
        (
            "feishu",
            "飞书",
            bool(settings.feishu_app_id and settings.feishu_app_secret),
        ),
        ("smtp", "邮件", bool(settings.smtp_user and settings.smtp_auth_code)),
    ]
    sources = []
    for key, name, configured in source_defs:
        row = source_rows.get(key)
        sources.append(
            {
                "source": key,
                "name": name,
                "configured": configured,
                "enabled": row.enabled if row else True,
                "last_status": row.last_status if row else None,
                "last_run_at": row.last_run_at.isoformat() if row and row.last_run_at else None,
                "last_error": row.last_error if row else None,
            }
        )

    last_run = (
        await session.execute(
            select(CollectionRun).order_by(CollectionRun.id.desc()).limit(1)
        )
    ).scalar_one_or_none()

    attendance_rows = (
        await session.execute(
            select(AttendanceRecord).where(AttendanceRecord.work_date == day)
        )
    ).scalars().all()
    attendance_status = Counter(row.status for row in attendance_rows)

    return {
        "date": day.isoformat(),
        "work_records": {
            "total": commits + len(tasks) + messages,
            "commits": commits,
            "tasks": len(tasks),
            "messages": messages,
        },
        "task_status": dict(task_status),
        "report_status": {
            "personal": {
                "total": len(personal),
                "statuses": dict(personal_status),
            },
            "team": {
                "total": len(team),
                "status": team[0].status if team else None,
            },
        },
        "recent_reports": [
            {
                "id": report.id,
                "report_date": report.report_date.isoformat(),
                "report_type": report.report_type,
                "member_name": members.get(report.member_id) if report.member_id else None,
                "status": report.status,
                "current_version": report.current_version,
            }
            for report in recent_reports
        ],
        "sources": sources,
        "feishu_mode": "mock" if settings.feishu_use_mock else "live",
        "last_run": (
            {
                "id": last_run.id,
                "run_type": last_run.run_type,
                "status": last_run.status,
                "started_at": last_run.started_at.isoformat() if last_run.started_at else None,
                "finished_at": last_run.finished_at.isoformat() if last_run.finished_at else None,
                "records_count": last_run.records_count,
                "error_message": last_run.error_message,
            }
            if last_run
            else None
        ),
        "attendance": {
            "total": len(attendance_rows),
            "statuses": dict(attendance_status),
        },
    }
