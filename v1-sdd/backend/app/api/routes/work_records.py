"""统一工作记录接口。"""

from datetime import date

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_session
from app.services.factory import build_orchestrator
from app.services.work_records import list_work_records

router = APIRouter(tags=["work-records"])


class CollectRequest(BaseModel):
    date: date


@router.get("/work-records")
async def work_records(
    record_type: str | None = Query(None, alias="type"),
    source: str | None = None,
    member_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    q: str | None = None,
    limit: int = 100,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
) -> dict:
    return await list_work_records(
        session,
        record_type=record_type,
        source=source,
        member_id=member_id,
        date_from=date_from,
        date_to=date_to,
        query=q,
        limit=min(limit, 500),
        offset=max(offset, 0),
    )


@router.post("/work-records/collect")
async def collect_work_records(
    payload: CollectRequest,
    session: AsyncSession = Depends(get_session),
) -> dict:
    orchestrator = build_orchestrator(session, get_settings())
    return await orchestrator.run(payload.date, push=False)
