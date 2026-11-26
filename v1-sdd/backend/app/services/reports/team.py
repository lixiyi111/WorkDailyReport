"""团队日报生成。"""

from datetime import date

from app.models import Member
from app.services.attribution import AttributedItem
from app.services.reports.personal import GeneratedReport
from app.services.reports.renderer import render_document


class TeamReportGenerator:
    def generate(
        self,
        report_date: date,
        members_reports: list[tuple[Member, GeneratedReport]],
        collaboration_items: list[tuple[Member, AttributedItem]],
        risks: list[str] | None = None,
    ) -> GeneratedReport:
        total_commits = sum(g.summary.get("commits", 0) for _, g in members_reports)
        total_tasks = sum(g.summary.get("tasks", 0) for _, g in members_reports)
        total_messages = sum(g.summary.get("messages", 0) for _, g in members_reports)
        no_output = sum(1 for _, g in members_reports if g.summary.get("no_output"))

        overview = [
            f"- 参与成员：{len(members_reports)} 人",
            f"- 提交数：{total_commits}",
            f"- 任务数：{total_tasks}",
            f"- 群消息：{total_messages}",
            f"- 无产出成员：{no_output} 人",
        ]

        member_lines = [
            (
                f"- {member.name}：提交 {g.summary.get('commits', 0)}，"
                f"任务 {g.summary.get('tasks', 0)}，消息 {g.summary.get('messages', 0)}"
            )
            for member, g in members_reports
        ]

        collab_lines = [
            f"- {member.name}：{item.title}（{item.detail}）" if item.detail else f"- {member.name}：{item.title}"
            for member, item in collaboration_items
        ]

        risk_lines = [f"- {risk}" for risk in (risks or [])] or ["- 暂无"]

        content = render_document(
            f"团队日报（{report_date.isoformat()}）",
            [
                ("团队概览", overview),
                ("成员摘要", member_lines),
                ("协作成果", collab_lines or ["- 暂无"]),
                ("风险与阻塞", risk_lines),
            ],
        )
        return GeneratedReport(
            title=f"团队日报 {report_date.isoformat()}",
            content_md=content,
            summary={
                "members": len(members_reports),
                "commits": total_commits,
                "tasks": total_tasks,
                "messages": total_messages,
                "no_output": no_output,
            },
        )
