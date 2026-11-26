"""V2-031：飞书机器人推送（Mock 跳过、真实发送）。"""

import json
from datetime import date

import httpx

from app.services.pushers.feishu_bot import FeishuBotPusher
from app.services.reports.types import GeneratedReport

REPORT = GeneratedReport(
    report_date=date(2026, 11, 6),
    report_type="team",
    member_id=None,
    member_name="全组",
    content_md="# 团队日报（2026-11-06）\n",
    summary={},
    items=[],
)


async def test_feishu_push_skipped_in_mock() -> None:
    pusher = FeishuBotPusher(app_id="", app_secret="", use_mock=True)
    result = await pusher.push(REPORT, "oc_1")

    assert result.skipped is True
    assert result.success is True
    assert result.attempts == 0


async def test_feishu_push_sends_to_chat() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/tenant_access_token/internal"):
            return httpx.Response(
                200, json={"code": 0, "tenant_access_token": "t-test"}
            )
        assert request.url.params["receive_id_type"] == "chat_id"
        body = json.loads(request.content)
        assert body["receive_id"] == "oc_1"
        text = json.loads(body["content"])["text"]
        assert "团队日报" in text
        return httpx.Response(200, json={"code": 0, "data": {}})

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        pusher = FeishuBotPusher(
            app_id="cli_test",
            app_secret="secret",
            use_mock=False,
            client=client,
        )
        result = await pusher.push(REPORT, "oc_1")

    assert result.success is True
    assert result.skipped is False
    assert result.attempts == 1
