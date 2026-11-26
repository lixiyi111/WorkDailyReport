"""数据源状态与推送日志接口。"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models import PushLog, SourceSyncState

router = APIRouter(tags=["sources"])


@router.get("/sources/status")
async def source_status(session: AsyncSession = Depends(get_session)) -> list[dict]:
    rows = (
        await session.execute(select(SourceSyncState).order_by(SourceSyncState.id))
    ).scalars().all()
    return [
        {
            "id": row.id,
            "source": row.source,
            "resource_key": row.resource_key,
            "last_cursor": row.last_cursor,
            "last_synced_at": row.last_synced_at.isoformat() if row.last_synced_at else None,
            "status": row.status,
            "error_message": row.error_message,
        }
        for row in rows
    ]


@router.get("/push-logs")
async def push_logs(session: AsyncSession = Depends(get_session)) -> list[dict]:
    rows = (
        await session.execute(select(PushLog).order_by(PushLog.id.desc()).limit(100))
    ).scalars().all()
    return [
        {
            "id": row.id,
            "report_id": row.report_id,
            "channel": row.channel,
            "target": row.target,
            "status": row.status,
            "attempt": row.attempt,
            "error_message": row.error_message,
            "sent_at": row.sent_at.isoformat(),
        }
        for row in rows
    ]
