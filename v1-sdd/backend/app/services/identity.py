"""成员身份解析：GitHub / 飞书身份 → 成员。"""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import IdentityUnmatched, Member, MemberIdentity


@dataclass
class ResolvedIdentity:
    identity_id: int | None
    member_id: int | None
    matched_by: str | None = None


class IdentityResolver:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def resolve(
        self,
        provider: str,
        external_id: str,
        *,
        external_username: str | None = None,
        email: str | None = None,
        source_type: str = "",
        source_id: str = "",
    ) -> ResolvedIdentity:
        external_id = external_id or (email or external_username or "")
        if not external_id:
            return ResolvedIdentity(None, None)

        result = await self.session.execute(
            select(MemberIdentity).where(
                MemberIdentity.provider == provider,
                MemberIdentity.external_id == external_id,
            )
        )
        identity = result.scalar_one_or_none()
        if identity:
            return ResolvedIdentity(identity.id, identity.member_id, "identity")

        if email:
            result = await self.session.execute(select(Member).where(Member.email == email))
            member = result.scalar_one_or_none()
            if member:
                identity = MemberIdentity(
                    member_id=member.id,
                    provider=provider,
                    external_id=external_id,
                    external_username=external_username,
                    verified=False,
                )
                self.session.add(identity)
                await self.session.flush()
                return ResolvedIdentity(identity.id, member.id, "email")

        if source_type and source_id:
            result = await self.session.execute(
                select(IdentityUnmatched).where(
                    IdentityUnmatched.provider == provider,
                    IdentityUnmatched.external_id == external_id,
                    IdentityUnmatched.source_type == source_type,
                    IdentityUnmatched.source_id == source_id,
                )
            )
            if result.scalar_one_or_none() is None:
                self.session.add(
                    IdentityUnmatched(
                        provider=provider,
                        external_id=external_id,
                        external_name=external_username,
                        source_type=source_type,
                        source_id=source_id,
                    )
                )
                await self.session.flush()

        return ResolvedIdentity(None, None)
