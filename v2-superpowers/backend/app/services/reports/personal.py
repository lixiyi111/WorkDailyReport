"""个人日报：四段式、无产出兜底、稳定排序。"""

from __future__ import annotations

from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

from app.services.attribution import AttributedItem
from app.services.collectors.attendance import AttendanceRecord
from app.services.reports.renderer import render_document
from app.services.reports.types import GeneratedReport

_STATUS_LABELS = {
    "normal": "正常",
    "late": "迟到",
    "early": "早退",
    "absent": "缺勤",
    "leave": "请假",
    "holiday": "节假日",
}
_SHANGHAI = ZoneInfo("Asia/Shanghai")


def _format_local(value: datetime | None) -> str:
    if value is None:
        return "—"
    return value.replace(tzinfo=UTC).astimezone(_SHANGHAI).strftime("%H:%M")


class PersonalReportGenerator:
    def generate(
        self,
        *,
        member_id: int,
        member_name: str | None,
        report_date: date,
        items: list[AttributedItem],
        attendance: AttendanceRecord | None = None,
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

        sections = [
            (
                "今日完成",
                [self._render_line(item) for item in today] or ["- 无产出"],
            ),
            (
                "协作贡献",
                [self._render_line(item) for item in collab] or ["- 无"],
            ),
            ("考勤", self._attendance_lines(attendance)),
            ("问题与阻塞", ["- 暂未发现阻塞（可手工补充）"]),
            ("明日计划", ["- 待补充（可手工编辑）"]),
        ]
        content = render_document(
            f"{member_name or '成员'} · 个人日报（{report_date.isoformat()}）",
            sections,
        )
        summary = {
            "commits": self._distinct_count(ordered, "commit"),
            "tasks": self._distinct_count(ordered, "task"),
            "messages": self._distinct_count(ordered, "message"),
            "total": len(ordered),
        }
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
    def _render_line(item: AttributedItem) -> str:
        return f"- [{item.source_type}] {item.title}（{item.attribution_role}）"

    @staticmethod
    def _attendance_lines(attendance: AttendanceRecord | None) -> list[str]:
        if attendance is None:
            return ["- 无考勤记录"]
        return [
            f"- 状态：{_STATUS_LABELS.get(attendance.status, attendance.status)}",
            f"- 上班：{_format_local(attendance.check_in_at)}",
            f"- 下班：{_format_local(attendance.check_out_at)}",
        ]

    @staticmethod
    def _distinct_count(items: list[AttributedItem], source_type: str) -> int:
        return len({item.source_id for item in items if item.source_type == source_type})
