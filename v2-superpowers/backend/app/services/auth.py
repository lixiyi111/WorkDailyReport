"""认证：PBKDF2 密码哈希、JWT、角色依赖与默认账号。"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_session
from app.models.entities import AppUser

bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str, iterations: int = 200_000) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return (
        f"pbkdf2_sha256${iterations}$"
        f"{base64.b64encode(salt).decode()}$"
        f"{base64.b64encode(digest).decode()}"
    )


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, iterations, salt_b64, digest_b64 = stored.split("$")
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    salt = base64.b64decode(salt_b64)
    expected = base64.b64decode(digest_b64)
    actual = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt, int(iterations)
    )
    return hmac.compare_digest(actual, expected)


def create_access_token(user: AppUser) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.auth_secret, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.auth_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="无效或过期的令牌") from exc


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
) -> AppUser:
    if credentials is None:
        raise HTTPException(status_code=401, detail="未登录")
    payload = decode_access_token(credentials.credentials)
    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=401, detail="令牌格式错误") from exc
    user = await session.get(AppUser, user_id)
    if user is None or not user.active:
        raise HTTPException(status_code=401, detail="用户不存在或已停用")
    return user


def require_roles(*roles: str):
    async def dependency(
        user: AppUser = Depends(get_current_user),
    ) -> AppUser:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="权限不足")
        return user

    return dependency


def user_dict(user: AppUser) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "member_id": user.member_id,
    }


async def seed_default_users(session: AsyncSession) -> None:
    """按 .env 创建 admin / leader / member 演示账号；已存在则跳过。"""
    settings = get_settings()
    candidates = [
        (settings.auth_admin_username, settings.auth_admin_password, "admin", None),
        (
            settings.auth_leader_username,
            settings.auth_leader_password,
            "leader",
            None,
        ),
        (
            settings.auth_member_username,
            settings.auth_member_password,
            "member",
            settings.auth_member_id,
        ),
    ]
    for username, password, role, member_id in candidates:
        if not username or not password:
            continue
        existing = await session.scalar(
            select(AppUser).where(AppUser.username == username)
        )
        if existing is not None:
            continue
        session.add(
            AppUser(
                username=username,
                password_hash=hash_password(password),
                role=role,
                member_id=member_id,
            )
        )
    await session.commit()
