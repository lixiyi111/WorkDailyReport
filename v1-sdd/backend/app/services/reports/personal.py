"""个人日报生成。"""

from dataclasses import dataclass
from datetime import date

from app.models import Member
from app.services.attribution import AttributedItem
from app.services.reports.renderer import render_document


@dataclass
class GeneratedReport:
    title: str
    content_md: str
    summary: dict


def _bullet(items: list[AttributedItem]) -> list[str]:
    lines = []
    for item in items:
        suffix = f"（{item.detail}）" if item.detail else ""
        lines.append(f"- {item.title}{suffix}")
    return lines


class PersonalReportGenerator:
    def generate(
        self,
        member: Member,
        report_date: date,
        items: list[AttributedItem],
        open_tasks: list[str] | None = None,
        attendance: dict | None = None,
    ) -> GeneratedReport:
        done = [i for i in items if i.role in ("author", "owner") and i.category != "message"]
        collab = [i for i in items if i.role in ("reviewer", "participant") or i.category == "message"]
        summary = {
            "member_id": member.id,
            "member_name": member.name,
            "commits": sum(1 for i in items if i.category == "commit"),
            "tasks": sum(1 for i in items if i.category == "task"),
            "messages": sum(1 for i in items if i.category == "message"),
            "total": len(items),
            "no_output": len(items) == 0,
        }

        done_lines = _bullet(done) if done else ["- 无产出"]
        collab_lines = _bullet(collab) if collab else ["- 暂无"]
        plan_lines = [f"- {title}" for title in (open_tasks or [])] or [
            "- 待补充（可手工编辑）"
        ]

        sections = [
            ("今日完成", done_lines),
            ("协作贡献", collab_lines),
            ("问题与阻塞", ["- 暂无"]),
            ("明日计划", plan_lines),
        ]
        if attendance:
            status_map = {
                "normal": "正常",
                "late": "迟到",
                "early": "早退",
                "absent": "缺卡",
                "leave": "请假",
            }
            lines = [f"- 考勤：{status_map.get(attendance['status'], attendance['status'])}"]
            if attendance.get("late_minutes"):
                lines.append(f"- 迟到 {attendance['late_minutes']} 分钟")
            if attendance.get("early_minutes"):
                lines.append(f"- 早退 {attendance['early_minutes']} 分钟")
            sections.insert(2, ("考勤", lines))
            summary["attendance"] = attendance["status"]

        content = render_document(
            f"{member.name} 的个人日报（{report_date.isoformat()}）",
            sections,
        )
        return GeneratedReport(
            title=f"{member.name} 的个人日报",
            content_md=content,
            summary=summary,
        )
