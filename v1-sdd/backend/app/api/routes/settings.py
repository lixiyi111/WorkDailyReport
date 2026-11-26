"""系统设置接口（仅非敏感配置）。"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models import SystemSetting
from app.services.auth import require_roles

router = APIRouter(tags=["settings"], dependencies=[Depends(require_roles("admin", "leader"))])

DEFAULTS = {
    "timezone": "Asia/Shanghai",
    "auto_collect_time": "09:00",
    "auto_generate_time": "09:10",
    "auto_push_time": "09:15",
    "retention_days": "90",
    "ai_enabled": "false",
    "ai_model": "",
    "report_template": "个人日报四段式 + 团队日报四段式",
}


class SettingsUpdate(BaseModel):
    values: dict[str, str]


async def _read_settings(session: AsyncSession) -> dict[str, str]:
    data = dict(DEFAULTS)
    rows = (await session.execute(select(SystemSetting))).scalars().all()
    data.update({row.key: row.value for row in rows if row.key in DEFAULTS})
    return data


@router.get("/settings")
async def read_settings(session: AsyncSession = Depends(get_session)) -> dict:
    return await _read_settings(session)


@router.put("/settings", dependencies=[Depends(require_roles("admin"))])
async def update_settings(
    payload: SettingsUpdate,
    session: AsyncSession = Depends(get_session),
) -> dict:
    for key, value in payload.values.items():
        if key not in DEFAULTS:
            continue
        row = await session.get(SystemSetting, key)
        if row is None:
            row = SystemSetting(key=key, value=str(value))
            session.add(row)
        else:
            row.value = str(value)
    await session.commit()
    return await _read_settings(session)
