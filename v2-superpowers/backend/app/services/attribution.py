"""协作成果归属：按角色把原始记录归到成员，并按自然键去重。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RawRecord:
    source_type: str  # commit / task / message
    source_id: str
    title: str
    member_id: int | None
    role: str  # author / owner / participant / reviewer
    detail: str | None = None
    occurred_at: datetime | None = None


@dataclass(frozen=True)
class AttributedItem:
    member_id: int
    category: str
    title: str
    source_type: str
    source_id: str
    attribution_role: str
    detail: str | None = None
    occurred_at: datetime | None = None


class AttributionEngine:
    def attribute(self, records: list[RawRecord]) -> list[AttributedItem]:
        """按 (source_type, source_id, member_id, role) 去重，保持输入顺序。"""
        seen: set[tuple[str, str, int, str]] = set()
        items: list[AttributedItem] = []
        for record in records:
            if record.member_id is None:
                continue
            key = (
                record.source_type,
                record.source_id,
                record.member_id,
                record.role,
            )
            if key in seen:
                continue
            seen.add(key)
            items.append(
                AttributedItem(
                    member_id=record.member_id,
                    category=record.source_type,
                    title=record.title,
                    source_type=record.source_type,
                    source_id=record.source_id,
                    attribution_role=record.role,
                    detail=record.detail,
                    occurred_at=record.occurred_at,
                )
            )
        return items
