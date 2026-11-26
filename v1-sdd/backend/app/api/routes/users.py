"""账号管理（仅管理员）。"""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models import AppUser
from app.services.auth import hash_password, require_roles, user_dict

router = APIRouter(tags=["users"], dependencies=[Depends(require_roles("admin"))])


class UserCreate(BaseModel):
    username: str
    password: str
    role: Literal["admin", "leader", "member"] = "member"
    member_id: int | None = None


@router.get("/users")
async def list_users(session: AsyncSession = Depends(get_session)) -> list[dict]:
    rows = (
        await session.execute(select(AppUser).order_by(AppUser.id))
    ).scalars().all()
    return [user_dict(row) for row in rows]


@router.post("/users", status_code=201)
async def create_user(
    payload: UserCreate, session: AsyncSession = Depends(get_session)
) -> dict:
    existing = (
        await session.execute(select(AppUser).where(AppUser.username == payload.username))
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="用户名已存在")
    user = AppUser(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=payload.role,
        member_id=payload.member_id,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user_dict(user)
