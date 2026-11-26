"""推送层公共类型与协议。"""

from dataclasses import dataclass
from typing import Protocol


@dataclass
class PushResult:
    channel: str
    target: str
    success: bool
    attempt: int = 1
    error: str | None = None


class Pusher(Protocol):
    channel: str

    async def push(self, subject: str, content: str, target: str) -> PushResult: ...
