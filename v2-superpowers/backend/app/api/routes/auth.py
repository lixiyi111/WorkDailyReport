"""登录与当前用户接口。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.entities import AppUser
from app.services.auth import (
    create_access_token,
    get_current_user,
    user_dict,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginIn(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(
    body: LoginIn, session: AsyncSession = Depends(get_session)
) -> dict:
    user = await session.scalar(
        select(AppUser).where(AppUser.username == body.username)
    )
    if (
        user is None
        or not user.active
        or not verify_password(body.password, user.password_hash)
    ):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return {
        "access_token": create_access_token(user),
        "token_type": "bearer",
        "user": user_dict(user),
    }


@router.get("/me")
async def me(user: AppUser = Depends(get_current_user)) -> dict:
    return user_dict(user)
