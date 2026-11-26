"""日报查询、编辑、生成与推送接口。"""

from __future__ import annotations

from dataclasses import asdict
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_session
from app.models.entities import (
    AppUser,
    DailyReport,
    Member,
    PushLog,
    ReportItem,
    ReportVersion,
    utcnow,
)
from app.schemas.report import GenerateIn, PushIn, ReportEditIn
from app.services.auth import get_current_user, require_roles
from app.services.factory import build_collectors, build_pushers
from app.services.orchestrator import DailyReportOrchestrator
from app.services.reports.types import GeneratedReport

router = APIRouter(prefix="/reports", tags=["reports"])


async def _detail(session: AsyncSession, report: DailyReport) -> dict:
    member_name = None
    if report.member_id:
        member_name = await session.scalar(
            select(Member.name).where(Member.id == report.member_id)
        )
    items = (
        await session.scalars(
            select(ReportItem)
            .where(ReportItem.report_id == report.id)
            .order_by(ReportItem.sort_order, ReportItem.id)
        )
    ).all()
    return {
        "id": report.id,
        "report_date": report.report_date.isoformat(),
        "report_type": report.report_type,
        "member_id": report.member_id,
        "member_name": member_name,
        "status": report.status,
        "current_version": report.current_version,
        "content_md": report.content_md,
        "summary": report.summary_json or {},
        "items": [
            {
                "id": item.id,
                "category": item.category,
                "title": item.title,
                "detail": item.detail,
                "source_type": item.source_type,
                "source_id": item.source_id,
                "attribution_role": item.attribution_role,
                "sort_order": item.sort_order,
            }
            for item in items
        ],
    }


@router.get("")
async def list_reports(
    date_: date | None = Query(None, alias="date"),
    report_type: str | None = None,
    member_id: int | None = None,
    user: AppUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    stmt = (
        select(DailyReport, Member.name)
        .outerjoin(Member, DailyReport.member_id == Member.id)
        .order_by(DailyReport.report_date.desc(), DailyReport.id)
    )
    if user.role == "member":
        stmt = stmt.where(
            or_(
                DailyReport.report_type == "team",
                DailyReport.member_id == user.member_id,
            )
        )
    if date_ is not None:
        stmt = stmt.where(DailyReport.report_date == date_)
    if report_type is not None:
        stmt = stmt.where(DailyReport.report_type == report_type)
    if member_id is not None:
        stmt = stmt.where(DailyReport.member_id == member_id)

    rows = (await session.execute(stmt)).all()
    return [
        {
            "id": report.id,
            "report_date": report.report_date.isoformat(),
            "report_type": report.report_type,
            "member_id": report.member_id,
            "member_name": member_name,
            "status": report.status,
            "current_version": report.current_version,
            "summary": report.summary_json or {},
        }
        for report, member_name in rows
    ]


@router.post("/generate")
async def generate_reports(
    body: GenerateIn,
    _manager: AppUser = Depends(require_roles("admin", "leader")),
    session: AsyncSession = Depends(get_session),
) -> dict:
    settings = get_settings()
    orchestrator = DailyReportOrchestrator(
        session,
        collectors=build_collectors(settings),
        pushers=build_pushers(settings),
        email_targets=settings.report_recipients,
        feishu_chat_id=settings.feishu_report_chat_id,
    )
    summary = await orchestrator.run(body.report_date, push=body.push)
    return asdict(summary)


@router.get("/{report_id}")
async def get_report(
    report_id: int,
    user: AppUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> dict:
    report = await session.get(DailyReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="日报不存在")
    if (
        user.role == "member"
        and report.report_type == "personal"
        and report.member_id != user.member_id
    ):
        raise HTTPException(status_code=403, detail="无权查看该日报")
    return await _detail(session, report)


@router.put("/{report_id}")
async def edit_report(
    report_id: int,
    body: ReportEditIn,
    _manager: AppUser = Depends(require_roles("admin", "leader")),
    session: AsyncSession = Depends(get_session),
) -> dict:
    report = await session.get(DailyReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="日报不存在")

    report.current_version += 1
    report.content_md = body.content_md
    report.updated_at = utcnow()
    session.add(
        ReportVersion(
            report_id=report.id,
            version=report.current_version,
            content_md=body.content_md,
            editor=body.editor,
            change_note=body.change_note,
        )
    )
    await session.commit()
    return await _detail(session, report)


@router.post("/{report_id}/push")
async def push_report(
    report_id: int,
    body: PushIn,
    _manager: AppUser = Depends(require_roles("admin", "leader")),
    session: AsyncSession = Depends(get_session),
) -> dict:
    report = await session.get(DailyReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="日报不存在")

    settings = get_settings()
    member_name = None
    if report.member_id:
        member_name = await session.scalar(
            select(Member.name).where(Member.id == report.member_id)
        )
    generated = GeneratedReport(
        report_date=report.report_date,
        report_type=report.report_type,
        member_id=report.member_id,
        member_name=member_name,
        content_md=report.content_md,
        summary=report.summary_json or {},
        items=[],
    )

    results: list[dict] = []
    for pusher in build_pushers(settings):
        if body.channel != "all" and pusher.channel != body.channel:
            continue
        if pusher.channel == "email":
            target = settings.report_recipients
        elif pusher.channel == "feishu":
            target = settings.feishu_report_chat_id
        else:
            target = "console"
        if pusher.channel in ("email", "feishu") and not target:
            continue

        result = await pusher.push(generated, target)
        for attempt in range(1, result.attempts + 1):
            success = result.success and attempt == result.attempts
            session.add(
                PushLog(
                    report_id=report.id,
                    channel=result.channel,
                    target=result.target,
                    status="success" if success else "failed",
                    attempt=attempt,
                    error_message=None if success else result.error,
                )
            )
        results.append(
            {
                "channel": result.channel,
                "success": result.success,
                "skipped": result.skipped,
                "attempts": result.attempts,
                "error": result.error,
            }
        )

    await session.commit()
    return {"results": results}
