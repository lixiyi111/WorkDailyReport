"""成员身份解析：已验证绑定 > 邮箱精确匹配 > 用户名精确匹配。"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import IdentityUnmatched, Member, MemberIdentity


class IdentityResolver:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def resolve(
        self,
        provider: str,
        external_id: str,
        external_username: str | None = None,
        email: str | None = None,
    ) -> int | None:
        """返回成员 ID；未命中返回 None（由调用方决定是否记录未归属）。"""
        identity = await self.session.scalar(
            select(MemberIdentity).where(
                MemberIdentity.provider == provider,
                MemberIdentity.external_id == external_id,
            )
        )
        if identity is not None:
            return identity.member_id

        member: Member | None = None
        if email:
            member = await self.session.scalar(
                select(Member).where(Member.email == email)
            )

        if member is None and external_username:
            member = await self.session.scalar(
                select(Member).where(Member.name == external_username)
            )
            if member is None:
                identity = await self.session.scalar(
                    select(MemberIdentity).where(
                        MemberIdentity.external_username == external_username
                    )
                )
                if identity is not None:
                    return identity.member_id

        if member is None:
            return None

        self.session.add(
            MemberIdentity(
                member_id=member.id,
                provider=provider,
                external_id=external_id,
                external_username=external_username,
                verified=False,
            )
        )
        await self.session.flush()
        return member.id

    async def record_unmatched(
        self,
        provider: str,
        external_id: str,
        external_name: str | None,
        source_type: str,
        source_id: str,
    ) -> None:
        """按 (provider, external_id, source_type, source_id) 幂等记录未归属。"""
        exists = await self.session.scalar(
            select(IdentityUnmatched.id).where(
                IdentityUnmatched.provider == provider,
                IdentityUnmatched.external_id == external_id,
                IdentityUnmatched.source_type == source_type,
                IdentityUnmatched.source_id == source_id,
            )
        )
        if exists is not None:
            return
        self.session.add(
            IdentityUnmatched(
                provider=provider,
                external_id=external_id,
                external_name=external_name,
                source_type=source_type,
                source_id=source_id,
            )
        )
        await self.session.flush()
