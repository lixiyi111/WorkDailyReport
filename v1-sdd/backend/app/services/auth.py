"""登录、JWT 与角色权限。"""

import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import get_session, get_session_factory
from app.models import AppUser

ALGORITHM = "HS256"
bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    iterations = 200_000
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return (
        f"pbkdf2_sha256${iterations}$"
        f"{base64.b64encode(salt).decode()}$"
        f"{base64.b64encode(digest).decode()}"
    )


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_b64, digest_b64 = encoded.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.b64decode(salt_b64)
        expected = base64.b64decode(digest_b64)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(iterations))
        return hmac.compare_digest(digest, expected)
    except (ValueError, TypeError):
        return False


def create_access_token(user: AppUser) -> str:
    settings = get_settings()
    if not settings.auth_secret:
        raise RuntimeError("AUTH_SECRET 未配置")
    now = datetime.now(UTC)
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "iat": now,
        "exp": now + timedelta(minutes=settings.auth_token_expire_minutes),
    }
    return jwt.encode(payload, settings.auth_secret, algorithm=ALGORITHM)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
) -> AppUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(
            credentials.credentials, get_settings().auth_secret, algorithms=[ALGORITHM]
        )
        user_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已失效",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    user = await session.get(AppUser, user_id)
    if user is None or not user.active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号不可用")
    return user


def require_roles(*roles: str):
    async def dependency(user: AppUser = Depends(get_current_user)) -> AppUser:
        if roles and user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")
        return user

    return dependency


def user_dict(user: AppUser) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "member_id": user.member_id,
        "active": user.active,
    }


async def seed_default_users() -> None:
    settings = get_settings()
    accounts = [
        (settings.auth_admin_username, settings.auth_admin_password, "admin", None),
        (settings.auth_leader_username, settings.auth_leader_password, "leader", None),
        (
            settings.auth_member_username,
            settings.auth_member_password,
            "member",
            settings.auth_member_id,
        ),
    ]
    factory = get_session_factory()
    async with factory() as session:
        for username, password, role, member_id in accounts:
            if not username or not password:
                continue
            existing = (
                await session.execute(select(AppUser).where(AppUser.username == username))
            ).scalar_one_or_none()
            if existing is None:
                session.add(
                    AppUser(
                        username=username,
                        password_hash=hash_password(password),
                        role=role,
                        member_id=member_id,
                    )
                )
            elif role == "member" and existing.member_id is None and member_id:
                existing.member_id = member_id
        await session.commit()
