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

        content = render_document(
            f"{member.name} 的个人日报（{report_date.isoformat()}）",
            [
                ("今日完成", done_lines),
                ("协作贡献", collab_lines),
                ("问题与阻塞", ["- 暂无"]),
                ("明日计划", plan_lines),
            ],
        )
        return GeneratedReport(
            title=f"{member.name} 的个人日报",
            content_md=content,
            summary=summary,
        )
