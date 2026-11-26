"""飞书任务采集。

流程：tenant_access_token → 分页拉取 task/v2/tasks → 按 task_id 去重 → 按窗口过滤。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import httpx

from app.core.contracts import AuthError, CollectionResult, SourceError, TimeWindow
from app.services.collectors.common import FetchError, parse_timestamp
from app.services.collectors.feishu_base import FeishuBase


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


class FeishuTaskCollector(FeishuBase):
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
        super().__init__(
            app_id,
            app_secret,
            client=client,
            base_url=base_url,
            timeout=timeout,
            attempts=attempts,
            retry_base_delay=retry_base_delay,
        )
        self.page_size = page_size

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
