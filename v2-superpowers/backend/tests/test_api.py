"""V2-050：REST API（日报、成员、身份、数据源、推送记录）。"""

from datetime import date

from sqlalchemy import select

from app.models.entities import (
    AppUser,
    AttendanceRecord,
    DailyReport,
    IdentityUnmatched,
    Member,
    MemberIdentity,
    PushLog,
    ReportItem,
    ReportVersion,
    SourceSyncState,
)
from app.services.auth import hash_password


async def _seed_reports(session):
    member = Member(name="王芳", email="wang@example.com")
    session.add(member)
    await session.flush()
    personal = DailyReport(
        report_date=date(2026, 11, 6),
        report_type="personal",
        scope_key=f"member:{member.id}",
        member_id=member.id,
        content_md="# 王芳 · 个人日报",
        summary_json={"total": 1},
    )
    team = DailyReport(
        report_date=date(2026, 11, 6),
        report_type="team",
        scope_key="team",
        content_md="# 团队日报",
        summary_json={"members": 1},
    )
    session.add_all([personal, team])
    await session.flush()
    session.add(
        ReportItem(
            report_id=personal.id,
            category="commit",
            title="修复登录接口",
            source_type="commit",
            source_id="sha-1",
            attribution_role="author",
        )
    )
    session.add(
        ReportVersion(
            report_id=personal.id,
            version=1,
            content_md="# 王芳 · 个人日报",
            editor="generator",
        )
    )
    await session.commit()
    return member, personal, team


async def test_reports_list_and_detail(session, admin_client) -> None:
    _, personal, _ = await _seed_reports(session)

    response = await admin_client.get("/api/reports")
    assert response.status_code == 200
    assert len(response.json()) == 2

    detail = await admin_client.get(f"/api/reports/{personal.id}")
    assert detail.status_code == 200
    data = detail.json()
    assert data["content_md"] == "# 王芳 · 个人日报"
    assert data["member_name"] == "王芳"
    assert data["items"][0]["title"] == "修复登录接口"


async def test_edit_creates_version(session, admin_client) -> None:
    _, personal, _ = await _seed_reports(session)

    response = await admin_client.put(
        f"/api/reports/{personal.id}",
        json={"content_md": "# 修订版", "editor": "王芳", "change_note": "手工修订"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["current_version"] == 2
    assert data["content_md"] == "# 修订版"

    version = await session.scalar(
        select(ReportVersion).where(
            ReportVersion.report_id == personal.id,
            ReportVersion.version == 2,
        )
    )
    assert version is not None


async def test_member_identity_binding(session, admin_client) -> None:
    member = Member(name="李四", email="li@example.com")
    session.add(member)
    await session.commit()

    response = await admin_client.post(
        f"/api/members/{member.id}/identities",
        json={
            "provider": "github",
            "external_id": "gh-1",
            "external_username": "lisi",
        },
    )
    assert response.status_code == 201

    identity = await session.scalar(
        select(MemberIdentity).where(MemberIdentity.external_id == "gh-1")
    )
    assert identity is not None
    assert identity.member_id == member.id


async def test_unmatched_identity_list(session, admin_client) -> None:
    session.add(
        IdentityUnmatched(
            provider="github",
            external_id="gh-x",
            external_name="unknown",
            source_type="commit",
            source_id="sha-x",
        )
    )
    await session.commit()

    response = await admin_client.get("/api/identities/unmatched")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["external_id"] == "gh-x"


async def test_sources_status_and_push_logs(session, admin_client) -> None:
    _, personal, _ = await _seed_reports(session)
    session.add(
        SourceSyncState(
            source="github",
            resource_key="2026-11-06",
            status="success",
        )
    )
    session.add(
        PushLog(
            report_id=personal.id,
            channel="console",
            target="console",
            status="success",
            attempt=1,
        )
    )
    await session.commit()

    sources = await admin_client.get("/api/sources/status")
    assert sources.status_code == 200
    assert sources.json()[0]["source"] == "github"

    logs = await admin_client.get("/api/push-logs")
    assert logs.status_code == 200
    assert logs.json()[0]["channel"] == "console"


async def test_attendance_api_member_scope(session, admin_client, client) -> None:
    member = Member(name="王芳", email="wang@example.com")
    other = Member(name="李四", email="li@example.com")
    session.add_all([member, other])
    await session.flush()
    session.add_all(
        [
            AttendanceRecord(
                member_id=member.id,
                attendance_date=date(2026, 11, 6),
                status="normal",
            ),
            AttendanceRecord(
                member_id=other.id,
                attendance_date=date(2026, 11, 6),
                status="late",
            ),
        ]
    )
    session.add(
        AppUser(
            username="member",
            password_hash=hash_password("member123"),
            role="member",
            member_id=member.id,
        )
    )
    await session.commit()

    admin_response = await admin_client.get("/api/attendance?date=2026-11-06")
    assert admin_response.status_code == 200
    assert len(admin_response.json()) == 2

    login = await client.post(
        "/api/auth/login",
        json={"username": "member", "password": "member123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    mine = await client.get("/api/attendance?date=2026-11-06", headers=headers)
    assert mine.status_code == 200
    assert len(mine.json()) == 1
    assert mine.json()[0]["member_id"] == member.id
