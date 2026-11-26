"""V2-011：飞书任务采集（token、分页、窗口、幂等、限流降级）。"""

from datetime import date, datetime

import httpx
import pytest

from app.core.contracts import AuthError
from app.core.timeutil import day_window
from app.services.collectors.feishu_tasks import FeishuTaskCollector

WINDOW = day_window(date(2026, 11, 6))


def _task(guid: str, updated_at: str, summary: str = "修复登录接口") -> dict:
    return {
        "guid": guid,
        "summary": summary,
        "status": "done",
        "completed_at": updated_at,
        "created_at": "2026-11-05T01:00:00Z",
        "updated_at": updated_at,
        "members": [
            {"id": "ou_owner", "role": "assignee", "type": "user"},
            {"id": "ou_helper", "role": "follower", "type": "user"},
        ],
    }


def _token_response() -> httpx.Response:
    return httpx.Response(
        200, json={"code": 0, "tenant_access_token": "t-test", "expire": 7200}
    )


async def test_feishu_task_collect_window() -> None:
    inside = _task("task-1", "2026-11-06T02:00:00Z")
    outside = _task("task-2", "2026-11-06T17:00:00Z")

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/tenant_access_token/internal"):
            assert request.method == "POST"
            return _token_response()
        assert request.headers["Authorization"] == "Bearer t-test"
        return httpx.Response(
            200,
            json={
                "code": 0,
                "data": {"items": [inside, outside], "has_more": False, "page_token": ""},
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        collector = FeishuTaskCollector(
            app_id="cli_test", app_secret="secret", client=client
        )
        result = await collector.collect(WINDOW)

    assert result.partial is False
    assert len(result.items) == 1
    task = result.items[0]
    assert task.task_id == "task-1"
    assert task.title == "修复登录接口"
    assert task.owner_external_id == "ou_owner"
    assert task.participants == ["ou_helper"]
    assert task.status_changed_at == datetime(2026, 11, 6, 2, 0)


async def test_feishu_task_dedup_by_guid() -> None:
    same = _task("task-1", "2026-11-06T02:00:00Z")

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/tenant_access_token/internal"):
            return _token_response()
        return httpx.Response(
            200,
            json={
                "code": 0,
                "data": {"items": [same, same], "has_more": False, "page_token": ""},
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        collector = FeishuTaskCollector(
            app_id="cli_test", app_secret="secret", client=client
        )
        result = await collector.collect(WINDOW)

    assert [item.task_id for item in result.items] == ["task-1"]


async def test_feishu_task_rate_limit_partial() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        if request.url.path.endswith("/tenant_access_token/internal"):
            return _token_response()
        calls += 1
        return httpx.Response(429, json={"code": 99991400, "msg": "rate limit"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        collector = FeishuTaskCollector(
            app_id="cli_test",
            app_secret="secret",
            client=client,
            retry_base_delay=0,
        )
        result = await collector.collect(WINDOW)

    assert calls == 3
    assert result.partial is True
    assert result.items == []
    assert result.errors[0].code == "RATE_LIMIT"


async def test_feishu_task_missing_credentials_raises_auth_error() -> None:
    collector = FeishuTaskCollector(app_id="", app_secret="")
    with pytest.raises(AuthError):
        await collector.collect(WINDOW)
