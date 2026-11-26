"""V2-012：飞书群消息采集（群过滤、窗口、去重、截断脱敏、限流）。"""

import json
from datetime import UTC, date, datetime

import httpx
import pytest

from app.core.contracts import AuthError
from app.core.timeutil import day_window
from app.services.collectors.feishu_messages import FeishuMessageCollector

WINDOW = day_window(date(2026, 11, 6))


def _ms(when: datetime) -> str:
    return str(int(when.replace(tzinfo=UTC).timestamp() * 1000))


def _message(message_id: str, text: str, when: datetime) -> dict:
    return {
        "message_id": message_id,
        "chat_id": "oc_1",
        "sender": {"id": "ou_sender", "id_type": "open_id", "sender_type": "user"},
        "create_time": _ms(when),
        "msg_type": "text",
        "body": {"content": json.dumps({"text": text}, ensure_ascii=False)},
    }


def _token_response() -> httpx.Response:
    return httpx.Response(
        200, json={"code": 0, "tenant_access_token": "t-test", "expire": 7200}
    )


async def test_message_chat_filter_and_parse() -> None:
    message = _message(
        "om_1", "今天修复了登录接口", datetime(2026, 11, 6, 1, 0)
    )

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/tenant_access_token/internal"):
            return _token_response()
        assert request.url.params["container_id_type"] == "chat"
        assert request.url.params["container_id"] == "oc_1"
        return httpx.Response(
            200,
            json={
                "code": 0,
                "data": {"items": [message], "has_more": False, "page_token": ""},
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        collector = FeishuMessageCollector(
            app_id="cli_test",
            app_secret="secret",
            chat_ids=["oc_1"],
            client=client,
        )
        result = await collector.collect(WINDOW)

    assert result.partial is False
    assert len(result.items) == 1
    item = result.items[0]
    assert item.message_id == "om_1"
    assert item.sender_external_id == "ou_sender"
    assert item.content_excerpt == "今天修复了登录接口"
    assert len(item.content_hash or "") == 64


async def test_message_truncated_and_desensitized() -> None:
    text = "联系 a@b.com 或 13800138000 " + "长" * 600
    message = _message("om_2", text, datetime(2026, 11, 6, 2, 0))

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/tenant_access_token/internal"):
            return _token_response()
        return httpx.Response(
            200,
            json={
                "code": 0,
                "data": {"items": [message], "has_more": False, "page_token": ""},
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        collector = FeishuMessageCollector(
            app_id="cli_test", app_secret="secret", chat_ids=["oc_1"], client=client
        )
        result = await collector.collect(WINDOW)

    excerpt = result.items[0].content_excerpt or ""
    assert len(excerpt) <= 500
    assert excerpt.endswith("…")
    assert "a@b.com" not in excerpt
    assert "13800138000" not in excerpt
    assert "***" in excerpt


async def test_message_dedup_by_id() -> None:
    same = _message("om_1", "重复消息", datetime(2026, 11, 6, 1, 0))

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
        collector = FeishuMessageCollector(
            app_id="cli_test", app_secret="secret", chat_ids=["oc_1"], client=client
        )
        result = await collector.collect(WINDOW)

    assert [item.message_id for item in result.items] == ["om_1"]


async def test_message_rate_limit_partial() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        if request.url.path.endswith("/tenant_access_token/internal"):
            return _token_response()
        calls += 1
        return httpx.Response(429, json={"code": 99991400, "msg": "rate limit"})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        collector = FeishuMessageCollector(
            app_id="cli_test",
            app_secret="secret",
            chat_ids=["oc_1"],
            client=client,
            retry_base_delay=0,
        )
        result = await collector.collect(WINDOW)

    assert calls == 3
    assert result.partial is True
    assert result.errors[0].code == "RATE_LIMIT"


async def test_message_missing_credentials_raises_auth_error() -> None:
    collector = FeishuMessageCollector(app_id="", app_secret="", chat_ids=["oc_1"])
    with pytest.raises(AuthError):
        await collector.collect(WINDOW)
