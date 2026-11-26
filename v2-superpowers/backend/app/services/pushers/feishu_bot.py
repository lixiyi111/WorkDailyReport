"""飞书机器人推送：Mock 模式跳过，真实模式发文本消息到群。"""

from __future__ import annotations

import json

import httpx

from app.core.contracts import AuthError
from app.services.collectors.common import FetchError
from app.services.collectors.feishu_base import FeishuBase
from app.services.pushers.base import AttemptHook, PushResult
from app.services.reports.types import GeneratedReport


class FeishuBotPusher(FeishuBase):
    channel = "feishu"

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        *,
        use_mock: bool = False,
        client: httpx.AsyncClient | None = None,
        base_url: str = "https://open.feishu.cn",
        timeout: float = 15.0,
        attempts: int = 3,
        retry_base_delay: float = 1.0,
        on_attempt: AttemptHook | None = None,
    ) -> None:
        super().__init__(
            app_id,
            app_secret,
            client=client,
            base_url=base_url,
            timeout=timeout,
            attempts=attempts,
            retry_base_delay=retry_base_delay,
        )
        self.use_mock = use_mock
        self.on_attempt = on_attempt

    async def push(self, report: GeneratedReport, target: str) -> PushResult:
        if self.use_mock or not self.app_id or not self.app_secret:
            return PushResult(
                channel=self.channel,
                target=target,
                success=True,
                attempts=0,
                skipped=True,
            )
        if self._client is not None:
            return await self._push(self._client, report, target)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await self._push(client, report, target)

    async def _push(
        self, client: httpx.AsyncClient, report: GeneratedReport, target: str
    ) -> PushResult:
        try:
            token = await self._get_token(client)
            await self._request_json(
                client,
                "POST",
                "/open-apis/im/v1/messages",
                token=token,
                params={"receive_id_type": "chat_id"},
                json_body={
                    "receive_id": target,
                    "msg_type": "text",
                    "content": json.dumps(
                        {"text": report.content_md}, ensure_ascii=False
                    ),
                },
            )
        except (FetchError, AuthError) as exc:
            if self.on_attempt is not None:
                await self.on_attempt(1, False, str(exc))
            return PushResult(
                channel=self.channel,
                target=target,
                success=False,
                attempts=1,
                error=str(exc),
            )

        if self.on_attempt is not None:
            await self.on_attempt(1, True, None)
        return PushResult(
            channel=self.channel,
            target=target,
            success=True,
            attempts=1,
        )
