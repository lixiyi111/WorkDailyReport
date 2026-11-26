"""飞书机器人推送。"""

import json

import httpx

from app.services.pushers.base import PushResult


class FeishuBotPusher:
    channel = "feishu"

    def __init__(self, app_id: str, app_secret: str, base_url: str = "https://open.feishu.cn") -> None:
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = base_url.rstrip("/")

    async def push(self, subject: str, content: str, target: str) -> PushResult:
        if not self.app_id or not self.app_secret:
            return PushResult(self.channel, target, False, error="飞书凭证未配置")
        if not target:
            return PushResult(self.channel, target, False, error="chat_id 为空")
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                token_response = await client.post(
                    f"{self.base_url}/open-apis/auth/v3/tenant_access_token/internal",
                    json={"app_id": self.app_id, "app_secret": self.app_secret},
                )
                token_response.raise_for_status()
                token_data = token_response.json()
                if token_data.get("code") != 0:
                    return PushResult(
                        self.channel,
                        target,
                        False,
                        error=f"鉴权失败 code={token_data.get('code')}",
                    )
                response = await client.post(
                    f"{self.base_url}/open-apis/im/v1/messages",
                    headers={"Authorization": f"Bearer {token_data['tenant_access_token']}"},
                    params={"receive_id_type": "chat_id"},
                    json={
                        "receive_id": target,
                        "msg_type": "text",
                        "content": json.dumps({"text": f"{subject}\n{content}"}, ensure_ascii=False),
                    },
                )
                response.raise_for_status()
                data = response.json()
                if data.get("code") != 0:
                    return PushResult(
                        self.channel,
                        target,
                        False,
                        error=f"发送失败 code={data.get('code')} msg={data.get('msg')}",
                    )
                return PushResult(self.channel, target, True)
        except Exception as exc:  # noqa: BLE001
            return PushResult(self.channel, target, False, error=type(exc).__name__)
