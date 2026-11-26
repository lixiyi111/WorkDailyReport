"""日报生成结果类型。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from app.services.attribution import AttributedItem


@dataclass(frozen=True)
class GeneratedReport:
    report_date: date
    report_type: str
    member_id: int | None
    member_name: str | None
    content_md: str
    summary: dict[str, int]
    items: list[AttributedItem] = field(default_factory=list)
