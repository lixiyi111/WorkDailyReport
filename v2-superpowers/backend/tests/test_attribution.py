"""V2-021：协作成果归属规则与去重。"""

from datetime import datetime

from app.services.attribution import AttributedItem, AttributionEngine, RawRecord


def test_attribution_roles() -> None:
    records = [
        RawRecord(
            source_type="commit",
            source_id="sha-1",
            title="修复登录接口",
            member_id=1,
            role="author",
            occurred_at=datetime(2026, 11, 6, 2, 0),
        ),
        RawRecord(
            source_type="task",
            source_id="task-1",
            title="登录联调",
            member_id=1,
            role="owner",
        ),
        RawRecord(
            source_type="task",
            source_id="task-1",
            title="登录联调",
            member_id=2,
            role="participant",
        ),
        RawRecord(
            source_type="message",
            source_id="msg-1",
            title="接口已联调",
            member_id=2,
            role="participant",
        ),
    ]

    items = AttributionEngine().attribute(records)

    assert len(items) == 4
    roles = {(item.member_id, item.source_id, item.attribution_role) for item in items}
    assert (1, "sha-1", "author") in roles
    assert (1, "task-1", "owner") in roles
    assert (2, "task-1", "participant") in roles
    assert (2, "msg-1", "participant") in roles
    assert all(isinstance(item, AttributedItem) for item in items)


def test_attribution_dedup() -> None:
    record = RawRecord(
        source_type="commit",
        source_id="sha-1",
        title="修复登录接口",
        member_id=1,
        role="author",
    )
    items = AttributionEngine().attribute([record, record])
    assert len(items) == 1


def test_attribution_skips_unmatched() -> None:
    record = RawRecord(
        source_type="commit",
        source_id="sha-x",
        title="未归属提交",
        member_id=None,
        role="author",
    )
    assert AttributionEngine().attribute([record]) == []
