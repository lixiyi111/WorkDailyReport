"""飞书任务采集。

流程：tenant_access_token → 分页拉取 task/v2/tasks → 按 task_id 去重 → 按窗口过滤。
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime

import httpx

from app.core.contracts import AuthError, CollectionResult, SourceError, TimeWindow
from app.services.collectors.common import FetchError, parse_timestamp


@dataclass(frozen=True)
class FeishuTaskRecord:
    task_id: str
    title: str
    owner_external_id: str | None
    participants: list[str]
    status: str
    status_changed_at: datetime | None
    created_at_source: datetime | None
    updated_at_source: datetime | None


class FeishuTaskCollector:
    source = "feishu_tasks"

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        *,
        client: httpx.AsyncClient | None = None,
        base_url: str = "https://open.feishu.cn",
        timeout: float = 15.0,
        page_size: int = 100,
        attempts: int = 3,
        retry_base_delay: float = 1.0,
    ) -> None:
        self.app_id = app_id
        self.app_secret = app_secret
        self._client = client
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.page_size = page_size
        self.attempts = attempts
        self.retry_base_delay = retry_base_delay

    async def collect(self, window: TimeWindow) -> CollectionResult[FeishuTaskRecord]:
        if not self.app_id or not self.app_secret:
            raise AuthError("缺少 FEISHU_APP_ID / FEISHU_APP_SECRET")
        if self._client is not None:
            return await self._collect(self._client, window)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await self._collect(client, window)

    async def _collect(
        self, client: httpx.AsyncClient, window: TimeWindow
    ) -> CollectionResult[FeishuTaskRecord]:
        try:
            token = await self._get_token(client)
        except FetchError as exc:
            return CollectionResult(
                items=[],
                partial=True,
                errors=[
                    SourceError(
                        source=self.source,
                        code=exc.code,
                        message=exc.message,
                        retryable=exc.retryable,
                    )
                ],
            )

        items: list[FeishuTaskRecord] = []
        errors: list[SourceError] = []
        partial = False
        seen: set[str] = set()
        page_token = ""

        while True:
            params: dict[str, object] = {"page_size": self.page_size}
            if page_token:
                params["page_token"] = page_token
            try:
                payload = await self._request_json(
                    client,
                    "GET",
                    "/open-apis/task/v2/tasks",
                    token=token,
                    params=params,
                )
            except FetchError as exc:
                errors.append(
                    SourceError(
                        source=self.source,
                        code=exc.code,
                        message=exc.message,
                        retryable=exc.retryable,
                    )
                )
                partial = True
                break

            data = payload.get("data") or {}
            for raw in data.get("items") or []:
                try:
                    record = self._parse(raw)
                except (KeyError, TypeError, ValueError) as exc:
                    errors.append(
                        SourceError(
                            source=self.source,
                            code="PARSE",
                            message=f"任务解析失败: {exc}",
                        )
                    )
                    partial = True
                    continue
                if record.status_changed_at and not window.contains(
                    record.status_changed_at
                ):
                    continue
                if record.task_id in seen:
                    continue
                seen.add(record.task_id)
                items.append(record)

            if not data.get("has_more"):
                break
            page_token = data.get("page_token") or ""
            if not page_token:
                break

        return CollectionResult(items=items, partial=partial, errors=errors)

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

    def _parse(self, raw: dict) -> FeishuTaskRecord:
        members = raw.get("members") or []
        owner = next(
            (member for member in members if member.get("role") == "assignee"), None
        )
        participants = [
            str(member["id"])
            for member in members
            if member.get("role") != "assignee" and member.get("id")
        ]
        updated_at = parse_timestamp(raw.get("updated_at"))
        status_changed_at = updated_at or parse_timestamp(raw.get("completed_at"))
        return FeishuTaskRecord(
            task_id=str(raw["guid"]),
            title=str(raw.get("summary") or "(无标题任务)"),
            owner_external_id=str(owner["id"]) if owner and owner.get("id") else None,
            participants=participants,
            status="done" if raw.get("completed_at") else str(raw.get("status", "todo")),
            status_changed_at=status_changed_at,
            created_at_source=parse_timestamp(raw.get("created_at")),
            updated_at_source=updated_at,
        )
