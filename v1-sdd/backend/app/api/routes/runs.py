"""运行记录接口。"""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_session
from app.models import CollectionRun
from app.services.auth import require_roles
from app.services.factory import build_orchestrator

router = APIRouter(tags=["runs"], dependencies=[Depends(require_roles("admin", "leader"))])


def _run_dict(run: CollectionRun) -> dict:
    return {
        "id": run.id,
        "run_type": run.run_type,
        "status": run.status,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "finished_at": run.finished_at.isoformat() if run.finished_at else None,
        "records_count": run.records_count,
        "error_message": run.error_message,
        "detail": run.detail_json,
    }


@router.get("/runs")
async def list_runs(
    limit: int = 20,
    session: AsyncSession = Depends(get_session),
) -> list[dict]:
    rows = (
        await session.execute(
            select(CollectionRun).order_by(CollectionRun.id.desc()).limit(min(limit, 100))
        )
    ).scalars().all()
    return [_run_dict(run) for run in rows]


@router.post("/runs/{run_id}/retry")
async def retry_run(
    run_id: int,
    session: AsyncSession = Depends(get_session),
) -> dict:
    run = await session.get(CollectionRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="运行记录不存在")
    report_date = (run.detail_json or {}).get("report_date")
    if not report_date:
        raise HTTPException(status_code=400, detail="该运行没有可重跑的日期")
    orchestrator = build_orchestrator(session, get_settings())
    return await orchestrator.run(date.fromisoformat(report_date), push=False)
