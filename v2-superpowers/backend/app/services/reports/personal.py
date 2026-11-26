"""个人日报：四段式、无产出兜底、稳定排序。"""

from __future__ import annotations

from datetime import date, datetime

from app.services.attribution import AttributedItem
from app.services.reports.types import GeneratedReport


class PersonalReportGenerator:
    def generate(
        self,
        *,
        member_id: int,
        member_name: str | None,
        report_date: date,
        items: list[AttributedItem],
    ) -> GeneratedReport:
        ordered = sorted(
            items,
            key=lambda item: (
                item.occurred_at or datetime.min,
                item.source_id,
                item.attribution_role,
            ),
        )
        today = [
            item
            for item in ordered
            if (item.source_type == "commit" and item.attribution_role == "author")
            or (item.source_type == "task" and item.attribution_role == "owner")
        ]
        collab = [
            item
            for item in ordered
            if item.attribution_role in ("participant", "reviewer")
        ]

        today_lines = self._render_lines(today, empty="- 无产出")
        collab_lines = self._render_lines(collab, empty="- 无")
        summary = {
            "commits": self._distinct_count(ordered, "commit"),
            "tasks": self._distinct_count(ordered, "task"),
            "messages": self._distinct_count(ordered, "message"),
            "total": len(ordered),
        }
        content = (
            f"# {member_name or '成员'} · 个人日报（{report_date.isoformat()}）\n\n"
            "## 今日完成\n"
            f"{today_lines}\n\n"
            "## 协作贡献\n"
            f"{collab_lines}\n\n"
            "## 问题与阻塞\n"
            "- 暂未发现阻塞（可手工补充）\n\n"
            "## 明日计划\n"
            "- 待补充（可手工编辑）\n"
        )
        return GeneratedReport(
            report_date=report_date,
            report_type="personal",
            member_id=member_id,
            member_name=member_name,
            content_md=content,
            summary=summary,
            items=ordered,
        )

    @staticmethod
    def _render_lines(items: list[AttributedItem], *, empty: str) -> str:
        if not items:
            return empty
        return "\n".join(
            f"- [{item.source_type}] {item.title}（{item.attribution_role}）"
            for item in items
        )

    @staticmethod
    def _distinct_count(items: list[AttributedItem], source_type: str) -> int:
        return len({item.source_id for item in items if item.source_type == source_type})
