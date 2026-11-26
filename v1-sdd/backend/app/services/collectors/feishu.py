"""飞书任务与群消息采集。"""

import hashlib
import json
from datetime import UTC, datetime

import httpx

from app.services.collectors.base import (
    AuthError,
    CollectionResult,
    RawMessageData,
    RawTaskData,
    SourceError,
    TimeWindow,
)


def _ms_to_dt(value: str | int | None) -> datetime | None:
    if value in (None, "", 0, "0"):
        return None
    ts = int(value)
    if ts > 10_000_000_000:  # 毫秒
        ts = ts / 1000
    return datetime.fromtimestamp(ts, tz=UTC).replace(tzinfo=None)


class FeishuClient:
    def __init__(self, app_id: str, app_secret: str, base_url: str = "https://open.feishu.cn") -> None:
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = base_url.rstrip("/")
        self._token: str | None = None
        self._expires_at: float = 0

    async def tenant_token(self, client: httpx.AsyncClient) -> str:
        import time

        if self._token and time.time() < self._expires_at - 60:
            return self._token
        if not self.app_id or not self.app_secret:
            raise AuthError("飞书 app_id / app_secret 未配置")
        response = await client.post(
            f"{self.base_url}/open-apis/auth/v3/tenant_access_token/internal",
            json={"app_id": self.app_id, "app_secret": self.app_secret},
        )
        response.raise_for_status()
        data = response.json()
        if data.get("code") != 0 or not data.get("tenant_access_token"):
            raise AuthError(f"飞书鉴权失败: code={data.get('code')} msg={data.get('msg')}")
        self._token = data["tenant_access_token"]
        self._expires_at = time.time() + int(data.get("expire", 7200))
        return self._token


class FeishuTaskCollector:
    source = "feishu_tasks"

    def __init__(self, client: FeishuClient) -> None:
        self.client = client

    async def collect(self, window: TimeWindow) -> CollectionResult[RawTaskData]:
        result: CollectionResult[RawTaskData] = CollectionResult()
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                token = await self.client.tenant_token(client)
                response = await client.get(
                    f"{self.client.base_url}/open-apis/task/v2/tasks",
                    headers={"Authorization": f"Bearer {token}"},
                    params={"page_size": 50},
                )
                response.raise_for_status()
                data = response.json()
                if data.get("code") != 0:
                    result.partial = True
                    result.errors.append(
                        SourceError(self.source, "API", f"code={data.get('code')} msg={data.get('msg')}")
                    )
                    return result
                for item in data.get("data", {}).get("items", []):
                    changed = _ms_to_dt(item.get("updated_at") or item.get("completed_at"))
                    created = _ms_to_dt(item.get("created_at"))
                    if changed and not (window.start <= changed < window.end):
                        if not (created and window.start <= created < window.end):
                            continue
                    members = item.get("members") or []
                    owner = members[0] if members else {}
                    result.items.append(
                        RawTaskData(
                            task_id=str(item.get("guid") or item.get("id")),
                            title=item.get("summary") or "(无标题任务)",
                            owner_external_id=str(owner.get("id")) if owner.get("id") else None,
                            owner_name=owner.get("name"),
                            owner_email=owner.get("email"),
                            participants=[str(m.get("id")) for m in members[1:] if m.get("id")],
                            status=str(item.get("status") or "open"),
                            status_changed_at=changed,
                            created_at_source=created,
                        )
                    )
            except AuthError as exc:
                raise exc
            except Exception as exc:  # noqa: BLE001
                result.partial = True
                result.errors.append(
                    SourceError(self.source, "NETWORK", type(exc).__name__)
                )
        return result


class FeishuMessageCollector:
    source = "feishu_messages"

    def __init__(self, client: FeishuClient, chat_ids: list[str]) -> None:
        self.client = client
        self.chat_ids = chat_ids

    async def collect(self, window: TimeWindow) -> CollectionResult[RawMessageData]:
        if not self.chat_ids:
            return CollectionResult(
                partial=True,
                errors=[SourceError(self.source, "CONFIG", "FEISHU_CHAT_IDS 未配置")],
            )
        result: CollectionResult[RawMessageData] = CollectionResult()
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                token = await self.client.tenant_token(client)
                for chat_id in self.chat_ids:
                    response = await client.get(
                        f"{self.client.base_url}/open-apis/im/v1/messages",
                        headers={"Authorization": f"Bearer {token}"},
                        params={
                            "container_id_type": "chat",
                            "container_id": chat_id,
                            "start_time": int(window.start.replace(tzinfo=UTC).timestamp()),
                            "end_time": int(window.end.replace(tzinfo=UTC).timestamp()),
                            "page_size": 50,
                        },
                    )
                    response.raise_for_status()
                    data = response.json()
                    if data.get("code") != 0:
                        result.partial = True
                        result.errors.append(
                            SourceError(
                                self.source,
                                "API",
                                f"{chat_id}: code={data.get('code')} msg={data.get('msg')}",
                            )
                        )
                        continue
                    for item in data.get("data", {}).get("items", []):
                        content = self._extract_text(item.get("body", {}).get("content"))
                        result.items.append(
                            RawMessageData(
                                message_id=str(item.get("message_id")),
                                chat_id=str(item.get("chat_id") or chat_id),
                                sender_external_id=str((item.get("sender") or {}).get("id") or "") or None,
                                sender_name=None,
                                sender_email=None,
                                sent_at=_ms_to_dt(item.get("create_time")) or window.start,
                                content=content,
                            )
                        )
            except AuthError as exc:
                raise exc
            except Exception as exc:  # noqa: BLE001
                result.partial = True
                result.errors.append(SourceError(self.source, "NETWORK", type(exc).__name__))
        return result

    @staticmethod
    def _extract_text(raw: str | None) -> str:
        if not raw:
            return ""
        try:
            payload = json.loads(raw)
            text = payload.get("text") or raw
        except json.JSONDecodeError:
            text = raw
        return str(text)[:500]

    @staticmethod
    def content_hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
