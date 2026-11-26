"""数据源配置、连通性测试、采集与推送日志。"""

import asyncio
import smtplib
from datetime import date

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.timeutil import now_utc
from app.db.session import get_session
from app.models import DataSource, PushLog, SourceSyncState
from app.services.collectors.base import AuthError
from app.services.collectors.feishu import FeishuClient
from app.services.factory import build_orchestrator

router = APIRouter(tags=["sources"])

ALLOWED_CONFIG = {
    "github": {"repos"},
    "feishu": {"chat_ids", "base_url"},
    "smtp": {"recipients"},
}


class SourceUpdate(BaseModel):
    enabled: bool | None = None
    config: dict | None = None


class SourceCollect(BaseModel):
    date: date


def _configured(source: str, settings) -> bool:
    if source == "github":
        return bool(settings.github_token)
    if source == "feishu":
        return bool(settings.feishu_app_id and settings.feishu_app_secret)
    if source == "smtp":
        return bool(settings.smtp_user and settings.smtp_auth_code)
    return False


def _source_dict(row: DataSource, settings) -> dict:
    return {
        "id": row.id,
        "source": row.source,
        "enabled": row.enabled,
        "config": row.config_json or {},
        "configured": _configured(row.source, settings),
        "last_run_at": row.last_run_at.isoformat() if row.last_run_at else None,
        "last_status": row.last_status,
        "last_error": row.last_error,
        "feishu_mode": "mock" if settings.feishu_use_mock else "live",
    }


async def _ensure_sources(session: AsyncSession, settings) -> None:
    existing = {
        row.source
        for row in (await session.execute(select(DataSource))).scalars().all()
    }
    defaults = {
        "github": {"repos": settings.github_repo_list},
        "feishu": {
            "chat_ids": settings.feishu_chat_id_list,
            "base_url": settings.feishu_base_url,
        },
        "smtp": {"recipients": settings.report_recipient_list},
    }
    added = False
    for source, config in defaults.items():
        if source not in existing:
            session.add(DataSource(source=source, enabled=True, config_json=config))
            added = True
    if added:
        await session.commit()


def _smtp_login(settings) -> None:
    with smtplib.SMTP_SSL(
        settings.smtp_host, settings.smtp_port, timeout=15
    ) as smtp:
        smtp.login(settings.smtp_user, settings.smtp_auth_code)


@router.get("/sources")
async def list_sources(session: AsyncSession = Depends(get_session)) -> list[dict]:
    settings = get_settings()
    await _ensure_sources(session, settings)
    rows = (
        await session.execute(select(DataSource).order_by(DataSource.id))
    ).scalars().all()
    return [_source_dict(row, settings) for row in rows]


@router.put("/sources/{source}")
async def update_source(
    source: str,
    payload: SourceUpdate,
    session: AsyncSession = Depends(get_session),
) -> dict:
    if source not in ALLOWED_CONFIG:
        raise HTTPException(status_code=404, detail="未知数据源")
    row = (
        await session.execute(select(DataSource).where(DataSource.source == source))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="数据源不存在")
    if payload.enabled is not None:
        row.enabled = payload.enabled
    if payload.config:
        filtered = {
            key: value
            for key, value in payload.config.items()
            if key in ALLOWED_CONFIG[source]
        }
        row.config_json = {**(row.config_json or {}), **filtered}
    await session.commit()
    return _source_dict(row, get_settings())


@router.post("/sources/{source}/test")
async def test_source(source: str) -> dict:
    settings = get_settings()
    if source == "github":
        if not settings.github_token:
            return {"ok": False, "message": "GITHUB_TOKEN 未配置"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{settings.github_api_base.rstrip('/')}/user",
                headers={
                    "Authorization": f"Bearer {settings.github_token}",
                    "Accept": "application/vnd.github+json",
                },
            )
        return {"ok": response.status_code == 200, "status_code": response.status_code}
    if source == "feishu":
        client = FeishuClient(
            settings.feishu_app_id,
            settings.feishu_app_secret,
            settings.feishu_base_url,
        )
        async with httpx.AsyncClient(timeout=15.0) as http:
            try:
                await client.tenant_token(http)
                return {"ok": True}
            except AuthError as exc:
                return {"ok": False, "message": str(exc)}
            except Exception as exc:  # noqa: BLE001
                return {"ok": False, "message": type(exc).__name__}
    if source == "smtp":
        if not settings.smtp_user or not settings.smtp_auth_code:
            return {"ok": False, "message": "SMTP 未配置"}
        try:
            await asyncio.to_thread(_smtp_login, settings)
            return {"ok": True}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "message": type(exc).__name__}
    raise HTTPException(status_code=404, detail="未知数据源")


@router.post("/sources/{source}/collect")
async def collect_source(
    source: str,
    payload: SourceCollect,
    session: AsyncSession = Depends(get_session),
) -> dict:
    if source not in ALLOWED_CONFIG:
        raise HTTPException(status_code=404, detail="未知数据源")
    row = (
        await session.execute(select(DataSource).where(DataSource.source == source))
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="数据源不存在")
    orchestrator = build_orchestrator(session, get_settings())
    result = await orchestrator.run(payload.date, push=False)
    row.last_run_at = now_utc()
    row.last_status = "partial" if result["errors"] else "success"
    row.last_error = "; ".join(
        f"{error['source']}: {error['message']}" for error in result["errors"]
    )[:1024] or None
    await session.commit()
    return result


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
