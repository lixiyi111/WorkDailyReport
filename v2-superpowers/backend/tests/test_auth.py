"""V2-051：登录、JWT 与成员可见范围。"""

from datetime import date

from app.models.entities import AppUser, DailyReport, Member
from app.services.auth import hash_password


async def _seed_user(
    session, username: str, password: str, role: str, member_id: int | None = None
) -> AppUser:
    user = AppUser(
        username=username,
        password_hash=hash_password(password),
        role=role,
        member_id=member_id,
    )
    session.add(user)
    await session.commit()
    return user


async def _login(client, username: str, password: str) -> dict[str, str]:
    response = await client.post(
        "/api/auth/login", json={"username": username, "password": password}
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def test_login_success(client, session) -> None:
    await _seed_user(session, "admin", "admin123", "admin")
    headers = await _login(client, "admin", "admin123")

    me = await client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200
    body = me.json()
    assert body["username"] == "admin"
    assert body["role"] == "admin"


async def test_login_wrong_password(client, session) -> None:
    await _seed_user(session, "admin", "admin123", "admin")
    response = await client.post(
        "/api/auth/login", json={"username": "admin", "password": "wrong"}
    )
    assert response.status_code == 401


async def test_anonymous_401(client) -> None:
    response = await client.get("/api/reports")
    assert response.status_code == 401


async def test_member_sees_own_and_team(client, session) -> None:
    own_member = Member(name="王芳", email="wang@example.com")
    other_member = Member(name="李四", email="li@example.com")
    session.add_all([own_member, other_member])
    await session.flush()

    own = DailyReport(
        report_date=date(2026, 11, 6),
        report_type="personal",
        scope_key=f"member:{own_member.id}",
        member_id=own_member.id,
        content_md="# 王芳",
        summary_json={},
    )
    other = DailyReport(
        report_date=date(2026, 11, 6),
        report_type="personal",
        scope_key=f"member:{other_member.id}",
        member_id=other_member.id,
        content_md="# 李四",
        summary_json={},
    )
    team = DailyReport(
        report_date=date(2026, 11, 6),
        report_type="team",
        scope_key="team",
        content_md="# 团队日报",
        summary_json={},
    )
    session.add_all([own, other, team])
    await session.commit()

    await _seed_user(session, "member", "member123", "member", own_member.id)
    headers = await _login(client, "member", "member123")

    listing = await client.get("/api/reports", headers=headers)
    assert listing.status_code == 200
    ids = {row["id"] for row in listing.json()}
    assert own.id in ids
    assert team.id in ids
    assert other.id not in ids

    assert (
        await client.get(f"/api/reports/{own.id}", headers=headers)
    ).status_code == 200
    assert (
        await client.get(f"/api/reports/{other.id}", headers=headers)
    ).status_code == 403


async def test_member_forbidden_admin_api(client, session) -> None:
    await _seed_user(session, "member", "member123", "member")
    headers = await _login(client, "member", "member123")

    response = await client.get("/api/sources/status", headers=headers)
    assert response.status_code == 403
