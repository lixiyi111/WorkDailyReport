"""飞书开放平台公共客户端：tenant token 与带重试的 JSON 请求。"""

from __future__ import annotations

import asyncio

import httpx

from app.core.contracts import AuthError
from app.services.collectors.common import FetchError


class FeishuBase:
    source = "feishu"

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        *,
        client: httpx.AsyncClient | None = None,
        base_url: str = "https://open.feishu.cn",
        timeout: float = 15.0,
        attempts: int = 3,
        retry_base_delay: float = 1.0,
    ) -> None:
        self.app_id = app_id
        self.app_secret = app_secret
        self._client = client
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.attempts = attempts
        self.retry_base_delay = retry_base_delay

    async def _get_token(self, client: httpx.AsyncClient) -> str:
        try:
            payload = await self._request_json(
                client,
                "POST",
                "/open-apis/auth/v3/tenant_access_token/internal",
                json_body={"app_id": self.app_id, "app_secret": self.app_secret},
            )
        except FetchError as exc:
            if exc.code == "RATE_LIMIT":
                raise
            raise AuthError(f"飞书 tenant_access_token 获取失败: {exc.message}") from exc
        token = payload.get("tenant_access_token")
        if not token:
            raise AuthError("飞书未返回 tenant_access_token")
        return str(token)

    async def _request_json(
        self,
        client: httpx.AsyncClient,
        method: str,
        path: str,
        *,
        token: str | None = None,
        json_body: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        url = f"{self.base_url}{path}"
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        for attempt in range(1, self.attempts + 1):
            try:
                response = await client.request(
                    method, url, headers=headers, json=json_body, params=params
                )
            except httpx.HTTPError as exc:
                raise FetchError("NETWORK", str(exc), retryable=True) from exc

            if response.status_code == 429:
                if attempt < self.attempts:
                    delay = self.retry_base_delay * (2 ** (attempt - 1))
                    if delay > 0:
                        await asyncio.sleep(delay)
                    continue
                raise FetchError("RATE_LIMIT", response.text, retryable=True)
            if response.status_code >= 400:
                raise FetchError(
                    "NETWORK",
                    f"飞书 HTTP {response.status_code}: {response.text}",
                    retryable=False,
                )

            payload = response.json()
            code = payload.get("code")
            if code not in (0, None):
                raise FetchError(
                    "API_ERROR",
                    f"飞书错误 {code}: {payload.get('msg', '')}",
                    retryable=False,
                )
            return payload

        raise FetchError("RATE_LIMIT", "重试次数耗尽", retryable=True)
