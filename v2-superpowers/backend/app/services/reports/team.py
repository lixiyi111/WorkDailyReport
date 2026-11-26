"""团队日报：团队概览 + 成员摘要 + 协作成果 + 风险与阻塞。"""

from __future__ import annotations

from datetime import date

from app.services.collectors.attendance import AttendanceRecord
from app.services.reports.renderer import render_document
from app.services.reports.types import GeneratedReport


class TeamReportGenerator:
    def generate(
        self,
        *,
        report_date: date,
        personal_reports: list[GeneratedReport],
        attendance_by_member: dict[int, AttendanceRecord] | None = None,
    ) -> GeneratedReport:
        ordered = sorted(
            personal_reports,
            key=lambda report: (report.member_name or "", report.member_id or 0),
        )
        commits = sum(report.summary.get("commits", 0) for report in ordered)
        tasks = sum(report.summary.get("tasks", 0) for report in ordered)
        messages = sum(report.summary.get("messages", 0) for report in ordered)

        collaboration: dict[tuple[str, str, str, str], set[str]] = {}
        for report in ordered:
            member_name = report.member_name or "未知成员"
            for item in report.items:
                if item.attribution_role not in ("participant", "reviewer"):
                    continue
                key = (
                    item.source_type,
                    item.source_id,
                    item.title,
                    item.attribution_role,
                )
                collaboration.setdefault(key, set()).add(member_name)

        overview_lines = [
            f"- 成员：{len(ordered)} 人",
            f"- 提交：{commits}",
            f"- 任务：{tasks}",
            f"- 消息：{messages}",
        ]
        attendance_counts = {"normal": 0, "late": 0, "leave": 0, "absent": 0}
        for record in (attendance_by_member or {}).values():
            if record.status == "normal":
                attendance_counts["normal"] += 1
            elif record.status in ("late", "early"):
                attendance_counts["late"] += 1
            elif record.status in ("leave", "holiday"):
                attendance_counts["leave"] += 1
            elif record.status == "absent":
                attendance_counts["absent"] += 1
        overview_lines.append(
            f"- 考勤：正常 {attendance_counts['normal']} · "
            f"迟到 {attendance_counts['late']} · "
            f"请假 {attendance_counts['leave']} · "
            f"缺勤 {attendance_counts['absent']}"
        )
        if ordered:
            member_lines = [
                f"- {report.member_name or '未知成员'}："
                f"{report.summary.get('commits', 0)} 提交 · "
                f"{report.summary.get('tasks', 0)} 任务 · "
                f"{report.summary.get('messages', 0)} 消息"
                for report in ordered
            ]
        else:
            member_lines = ["- 无成员数据"]

        collab_lines = [
            f"- [{key[0]}] {key[2]}（{key[3]}）：{'、'.join(sorted(names))}"
            for key, names in sorted(collaboration.items())
        ] or ["- 无"]

        sections = [
            ("团队概览", overview_lines),
            ("成员摘要", member_lines),
            ("协作成果", collab_lines),
            ("风险与阻塞", ["- 暂未发现阻塞（可手工补充）"]),
        ]
        content = render_document(f"团队日报（{report_date.isoformat()}）", sections)
        summary = {
            "members": len(ordered),
            "commits": commits,
            "tasks": tasks,
            "messages": messages,
            "collaboration": len(collaboration),
            "total": sum(report.summary.get("total", 0) for report in ordered),
        }
        return GeneratedReport(
            report_date=report_date,
            report_type="team",
            member_id=None,
            member_name="全组",
            content_md=content,
            summary=summary,
            items=[item for report in ordered for item in report.items],
        )
