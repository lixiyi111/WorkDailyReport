"""采集层公共类型与协议。"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol


class AuthError(Exception):
    """凭证缺失或不合法，无法继续采集。"""


@dataclass(frozen=True)
class TimeWindow:
    start: datetime  # naive UTC，含
    end: datetime    # naive UTC，不含
    tz: str = "Asia/Shanghai"


@dataclass
class SourceError:
    source: str
    code: str  # AUTH / RATE_LIMIT / NETWORK / PARSE / CONFIG
    message: str
    retryable: bool = False


@dataclass
class CollectionResult[T]:
    items: list[T] = field(default_factory=list)
    partial: bool = False
    errors: list[SourceError] = field(default_factory=list)
    cursor: str | None = None


class Collector(Protocol):
    source: str

    async def collect(self, window: TimeWindow) -> CollectionResult[Any]: ...


@dataclass
class RawCommitData:
    repo_full_name: str
    sha: str
    author_name: str
    author_email: str | None
    committed_at: datetime
    message: str
    branch: str | None = None
    url: str | None = None
    pr_number: int | None = None


@dataclass
class RawTaskData:
    task_id: str
    title: str
    owner_external_id: str | None
    owner_name: str | None
    owner_email: str | None
    participants: list[str] = field(default_factory=list)
    status: str = "open"
    status_changed_at: datetime | None = None
    created_at_source: datetime | None = None


@dataclass
class RawMessageData:
    message_id: str
    chat_id: str
    sender_external_id: str | None
    sender_name: str | None
    sender_email: str | None
    sent_at: datetime
    content: str
