"""V2-071：考勤采集器（Mock、聚合、限流、鉴权）。"""

from datetime import date, datetime

import httpx
import pytest

from app.core.contracts import AuthError
from app.core.timeutil import day_window
from app.services.collectors.attendance import (
    FeishuAttendanceCollector,
    MockAttendanceCollector,
)

WINDOW = day_window(date(2026, 11, 6))
EMAILS = ["wang@example.com", "li@example.com", "zhao@example.com"]


def _token_response() -> httpx.Response:
    return httpx.Response(
        200, json={"code": 0, "tenant_access_token": "t-test", "expire": 7200}
    )


async def test_mock_attendance_collect() -> None:
    result = await MockAttendanceCollector(EMAILS).collect(WINDOW)

    assert result.partial is False
    assert len(result.items) == 3
    assert {item.status for item in result.items} >= {"normal", "late", "leave"}
    assert all(item.attendance_date == date(2026, 11, 6) for item in result.items)


async def test_feishu_attendance_aggregates_by_member_date() -> None:
    """同一成员同一天多条打卡：最早上班、最晚下班、状态取最严重。"""

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/tenant_access_token/internal"):
            return _token_response()
        return httpx.Response(
            200,
            json={
                "code": 0,
                "data": {
                    "items": [
                        {
                            "id": "rec-1",
                            "user_id": "ou_1",
                            "check_date": "2026-11-06",
                            "status": "normal",
                            "check_in": "2026-11-06T09:00:00+08:00",
                            "check_out": "2026-11-06T18:00:00+08:00",
                        },
                        {
                            "id": "rec-2",
                            "user_id": "ou_1",
                            "check_date": "2026-11-06",
                            "status": "late",
                            "check_in": "2026-11-06T09:30:00+08:00",
                            "check_out": "2026-11-06T18:30:00+08:00",
                        },
                    ]
                },
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        collector = FeishuAttendanceCollector(
            "cli_test",
            "secret",
            member_external_ids=["ou_1"],
            client=client,
        )
        result = await collector.collect(WINDOW)

    assert len(result.items) == 1
    item = result.items[0]
    assert item.member_external_id == "ou_1"
    assert item.status == "late"
    assert item.check_in_at == datetime(2026, 11, 6, 1, 0)  # 09:00 CST
    assert item.check_out_at == datetime(2026, 11, 6, 10, 30)  # 18:30 CST


async def test_feishu_attendance_rate_limit_partial() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        if request.url.path.endswith("/tenant_access_token/internal"):
            return _token_response()
        calls += 1
        return httpx.Response(429, json={"code": 99991400, "msg": "rate limit"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        collector = FeishuAttendanceCollector(
            "cli_test",
            "secret",
            member_external_ids=["ou_1"],
            client=client,
            retry_base_delay=0,
        )
        result = await collector.collect(WINDOW)

    assert calls == 3
    assert result.partial is True
    assert result.errors[0].code == "RATE_LIMIT"


async def test_feishu_attendance_missing_credentials_raises_auth_error() -> None:
    collector = FeishuAttendanceCollector(
        "", "", member_external_ids=["ou_1"]
    )
    with pytest.raises(AuthError):
        await collector.collect(WINDOW)
