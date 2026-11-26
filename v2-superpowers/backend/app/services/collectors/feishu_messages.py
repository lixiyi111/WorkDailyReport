"""飞书群消息采集。

只采集配置的 chat_id；按 message_id 去重；内容截断到 500 字并脱敏。
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx

from app.core.contracts import AuthError, CollectionResult, SourceError, TimeWindow
from app.services.collectors.common import FetchError, parse_timestamp
from app.services.collectors.feishu_base import FeishuBase

_EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
_PHONE_RE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")


@dataclass(frozen=True)
class FeishuMessageRecord:
    message_id: str
    chat_id: str
    sender_external_id: str | None
    sender_name: str | None
    sent_at: datetime | None
    content_excerpt: str
    content_hash: str


def desensitize(text: str) -> str:
    """把邮箱与手机号替换为 ***。"""
    return _PHONE_RE.sub("***", _EMAIL_RE.sub("***", text))


def truncate(text: str, limit: int = 500) -> str:
    """超长内容截断并以省略号结尾。"""
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


class FeishuMessageCollector(FeishuBase):
    source = "feishu_messages"

    def __init__(
        self,
        app_id: str,
        app_secret: str,
        *,
        chat_ids: list[str],
        client: httpx.AsyncClient | None = None,
        base_url: str = "https://open.feishu.cn",
        timeout: float = 15.0,
        page_size: int = 50,
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
        self.chat_ids = chat_ids
        self.page_size = page_size

    async def collect(
        self, window: TimeWindow
    ) -> CollectionResult[FeishuMessageRecord]:
        if not self.app_id or not self.app_secret:
            raise AuthError("缺少 FEISHU_APP_ID / FEISHU_APP_SECRET")
        if not self.chat_ids:
            return CollectionResult(items=[])
        if self._client is not None:
            return await self._collect(self._client, window)
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            return await self._collect(client, window)

    async def _collect(
        self, client: httpx.AsyncClient, window: TimeWindow
    ) -> CollectionResult[FeishuMessageRecord]:
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

        items: list[FeishuMessageRecord] = []
        errors: list[SourceError] = []
        partial = False
        seen: set[str] = set()
        start_time = str(int(window.start.replace(tzinfo=UTC).timestamp()))
        end_time = str(int(window.end.replace(tzinfo=UTC).timestamp()))

        for chat_id in self.chat_ids:
            page_token = ""
            while True:
                params: dict[str, object] = {
                    "container_id_type": "chat",
                    "container_id": chat_id,
                    "start_time": start_time,
                    "end_time": end_time,
                    "page_size": self.page_size,
                }
                if page_token:
                    params["page_token"] = page_token
                try:
                    payload = await self._request_json(
                        client,
                        "GET",
                        "/open-apis/im/v1/messages",
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
                                message=f"消息解析失败: {exc}",
                            )
                        )
                        partial = True
                        continue
                    if record.sent_at and not window.contains(record.sent_at):
                        continue
                    if record.message_id in seen:
                        continue
                    seen.add(record.message_id)
                    items.append(record)

                if not data.get("has_more"):
                    break
                page_token = data.get("page_token") or ""
                if not page_token:
                    break

        return CollectionResult(items=items, partial=partial, errors=errors)

    def _parse(self, raw: dict) -> FeishuMessageRecord:
        sender = raw.get("sender") or {}
        text = self._extract_text((raw.get("body") or {}).get("content"))
        excerpt = desensitize(truncate(text))
        return FeishuMessageRecord(
            message_id=str(raw["message_id"]),
            chat_id=str(raw.get("chat_id") or ""),
            sender_external_id=str(sender["id"]) if sender.get("id") else None,
            sender_name=sender.get("name"),
            sent_at=parse_timestamp(raw.get("create_time")),
            content_excerpt=excerpt,
            content_hash=hashlib.sha256(excerpt.encode("utf-8")).hexdigest(),
        )

    @staticmethod
    def _extract_text(content: object) -> str:
        if not isinstance(content, str):
            return str(content or "")
        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            return content
        if isinstance(payload, dict):
            return str(payload.get("text") or payload.get("content") or content)
        return content
