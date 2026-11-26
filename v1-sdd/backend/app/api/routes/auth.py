"""登录与当前用户。"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models import AppUser
from app.services.auth import (
    create_access_token,
    get_current_user,
    user_dict,
    verify_password,
)

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/auth/login")
async def login(
    payload: LoginRequest, session: AsyncSession = Depends(get_session)
) -> dict:
    user = (
        await session.execute(select(AppUser).where(AppUser.username == payload.username))
    ).scalar_one_or_none()
    if user is None or not user.active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return {
        "access_token": create_access_token(user),
        "token_type": "bearer",
        "user": user_dict(user),
    }


@router.get("/auth/me")
async def me(user: AppUser = Depends(get_current_user)) -> dict:
    return user_dict(user)
