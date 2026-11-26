"""V2-002：ORM 模型、建表与幂等唯一键。"""

from datetime import date, datetime

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

from app.db.session import init_models, make_engine
from app.models.entities import DailyReport, RawCommit, Repository

EXPECTED_TABLES = {
    "app_users",
    "attendance_records",
    "daily_reports",
    "identity_unmatched",
    "member_identities",
    "members",
    "push_logs",
    "raw_commits",
    "raw_messages",
    "raw_tasks",
    "report_items",
    "report_versions",
    "repositories",
    "source_sync_state",
}


async def test_create_all_tables() -> None:
    """13 张核心表可在空库一次性建出。"""
    engine = make_engine("sqlite+aiosqlite:///:memory:")
    await init_models(engine)
    async with engine.connect() as conn:
        names = await conn.run_sync(lambda c: set(inspect(c).get_table_names()))
    assert names == EXPECTED_TABLES
    await engine.dispose()


async def test_report_unique_key(session) -> None:
    """同一日期、类型、范围只允许一份日报。"""
    session.add_all(
        [
            DailyReport(
                report_date=date(2026, 11, 6),
                report_type="team",
                scope_key="team",
                content_md="# 第一份",
            ),
            DailyReport(
                report_date=date(2026, 11, 6),
                report_type="team",
                scope_key="team",
                content_md="# 第二份",
            ),
        ]
    )
    with pytest.raises(IntegrityError):
        await session.commit()


async def test_commit_idempotency_key(session) -> None:
    """同一仓库的同一 SHA 只能入库一次。"""
    repo = Repository(owner="lixiyi111", name="WorkDailyReport")
    session.add(repo)
    await session.flush()

    for _ in range(2):
        session.add(
            RawCommit(
                repo_id=repo.id,
                sha="a" * 40,
                author_name="guandong",
                committed_at=datetime(2026, 11, 6, 10, 0),
                message="duplicate",
            )
        )
    with pytest.raises(IntegrityError):
        await session.commit()
