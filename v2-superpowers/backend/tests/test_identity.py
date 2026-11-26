"""V2-020：成员身份解析与未归属记录。"""

from sqlalchemy import func, select

from app.models.entities import IdentityUnmatched, Member, MemberIdentity
from app.services.identity import IdentityResolver


async def test_resolve_by_email(session) -> None:
    member = Member(name="王芳", email="wang@example.com")
    session.add(member)
    await session.flush()

    resolver = IdentityResolver(session)
    member_id = await resolver.resolve(
        "github", "gh-1", external_username="wang", email="wang@example.com"
    )

    assert member_id == member.id
    identity = await session.scalar(
        select(MemberIdentity).where(MemberIdentity.external_id == "gh-1")
    )
    assert identity is not None
    assert identity.member_id == member.id


async def test_existing_binding_takes_priority(session) -> None:
    member_a = Member(name="甲", email="a@example.com")
    member_b = Member(name="乙", email="b@example.com")
    session.add_all([member_a, member_b])
    await session.flush()
    session.add(
        MemberIdentity(
            member_id=member_a.id,
            provider="github",
            external_id="gh-1",
            verified=True,
        )
    )
    await session.flush()

    resolver = IdentityResolver(session)
    member_id = await resolver.resolve("github", "gh-1", email="b@example.com")

    assert member_id == member_a.id


async def test_resolve_by_username(session) -> None:
    member = Member(name="王芳", email="wang@example.com")
    session.add(member)
    await session.flush()

    resolver = IdentityResolver(session)
    member_id = await resolver.resolve("feishu", "ou-1", external_username="王芳")

    assert member_id == member.id


async def test_unmatched_written_once(session) -> None:
    resolver = IdentityResolver(session)
    assert await resolver.resolve("github", "gh-x") is None

    for _ in range(2):
        await resolver.record_unmatched(
            "github", "gh-x", "unknown", "commit", "sha-1"
        )

    count = await session.scalar(select(func.count()).select_from(IdentityUnmatched))
    assert count == 1
