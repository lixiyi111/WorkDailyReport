"""日报查询、编辑、生成与推送接口。"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_session
from app.models import AppUser, DailyReport, Member, PushLog, ReportItem, ReportVersion
from app.schemas import GenerateRequest, PushRequest, ReportUpdate
from app.services.auth import get_current_user, require_roles
from app.services.collectors import (
    MockFeishuMessageCollector,
    MockFeishuTaskCollector,
    MockGitHubCollector,
)
from app.services.demo import ensure_demo_members
from app.services.factory import build_orchestrator
from app.services.orchestrator import DailyReportOrchestrator
from app.services.pushers import ConsolePusher, EmailPusher, FeishuBotPusher

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[Depends(get_current_user)],
)


def _report_dict(
    report: DailyReport,
    items: list[ReportItem] | None = None,
    member_name: str | None = None,
) -> dict:
    data = {
        "id": report.id,
        "report_date": report.report_date.isoformat(),
        "report_type": report.report_type,
        "scope_key": report.scope_key,
        "member_id": report.member_id,
        "member_name": member_name,
        "status": report.status,
        "current_version": report.current_version,
        "content_md": report.content_md,
        "summary": report.summary_json,
        "generated_at": report.generated_at.isoformat(),
        "updated_at": report.updated_at.isoformat(),
    }
    if items is not None:
        data["items"] = [
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
        ]
    return data


@router.get("")
async def list_reports(
    report_date: date | None = Query(None, alias="date"),
    report_type: str | None = Query(None, alias="type"),
    member_id: int | None = None,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    user: AppUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    stmt = select(DailyReport)
    if report_date:
        stmt = stmt.where(DailyReport.report_date == report_date)
    if report_type:
        stmt = stmt.where(DailyReport.report_type == report_type)
    if member_id:
        stmt = stmt.where(DailyReport.member_id == member_id)
    if status:
        stmt = stmt.where(DailyReport.status == status)
    if date_from:
        stmt = stmt.where(DailyReport.report_date >= date_from)
    if date_to:
        stmt = stmt.where(DailyReport.report_date <= date_to)
    if user.role == "member":
        if user.member_id:
            stmt = stmt.where(
                or_(
                    DailyReport.report_type == "team",
                    DailyReport.member_id == user.member_id,
                )
            )
        else:
            stmt = stmt.where(DailyReport.report_type == "team")
    reports = (
        await session.execute(
            stmt.order_by(DailyReport.report_date.desc(), DailyReport.id.desc())
        )
    ).scalars().all()
    members = {
        member.id: member.name
        for member in (await session.execute(select(Member))).scalars().all()
    }
    return [
        _report_dict(report, member_name=members.get(report.member_id))
        for report in reports
    ]


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
    items = (
        await session.execute(
            select(ReportItem)
            .where(ReportItem.report_id == report_id)
            .order_by(ReportItem.sort_order)
        )
    ).scalars().all()
    member = await session.get(Member, report.member_id) if report.member_id else None
    return _report_dict(report, items, member.name if member else None)


@router.put("/{report_id}", dependencies=[Depends(require_roles("admin", "leader"))])
async def update_report(
    report_id: int,
    payload: ReportUpdate,
    session: AsyncSession = Depends(get_session),
) -> dict:
    report = await session.get(DailyReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="日报不存在")
    new_version = report.current_version + 1
    session.add(
        ReportVersion(
            report_id=report.id,
            version=new_version,
            content_md=payload.content_md,
            editor=payload.editor,
            change_note=payload.change_note,
        )
    )
    report.content_md = payload.content_md
    report.current_version = new_version
    report.status = "draft"
    await session.commit()
    member = await session.get(Member, report.member_id) if report.member_id else None
    return _report_dict(report, member_name=member.name if member else None)


@router.post("/generate", dependencies=[Depends(require_roles("admin", "leader"))])
async def generate_report(
    payload: GenerateRequest, session: AsyncSession = Depends(get_session)
) -> dict:
    settings = get_settings()
    if payload.demo:
        members = await ensure_demo_members(session)
        emails = [member.email for member in members]
        collectors = [
            MockGitHubCollector(emails),
            MockFeishuTaskCollector(emails),
            MockFeishuMessageCollector(emails),
        ]
        orchestrator = DailyReportOrchestrator(
            session=session,
            collectors=collectors,
            pushers=[ConsolePusher()],
            settings=settings,
        )
    else:
        orchestrator = build_orchestrator(session, settings)
    return await orchestrator.run(payload.report_date, push=payload.push)


@router.post("/{report_id}/push", dependencies=[Depends(require_roles("admin", "leader"))])
async def push_report(
    report_id: int,
    payload: PushRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    report = await session.get(DailyReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="日报不存在")
    settings = get_settings()
    if payload.channel == "console":
        pusher = ConsolePusher()
        default_target = "stdout"
    elif payload.channel == "email":
        pusher = EmailPusher(
            settings.smtp_host,
            settings.smtp_port,
            settings.smtp_user,
            settings.smtp_auth_code,
            settings.smtp_from_name,
        )
        default_target = ",".join(settings.report_recipient_list)
    elif payload.channel == "feishu":
        pusher = FeishuBotPusher(settings.feishu_app_id, settings.feishu_app_secret)
        default_target = settings.feishu_report_chat_id
    else:
        raise HTTPException(status_code=400, detail="不支持的推送渠道")

    target = payload.target or default_target
    if not target:
        raise HTTPException(status_code=400, detail="推送目标为空")

    label = "团队日报" if report.report_type == "team" else "个人日报"
    subject = f"{label} {report.report_date.isoformat()}"
    result = await pusher.push(subject, report.content_md, target)
    session.add(
        PushLog(
            report_id=report.id,
            channel=result.channel,
            target=result.target,
            status="success" if result.success else "failed",
            attempt=result.attempt,
            error_message=result.error,
        )
    )
    await session.commit()
    return {
        "channel": result.channel,
        "target": result.target,
        "success": result.success,
        "error": result.error,
    }
