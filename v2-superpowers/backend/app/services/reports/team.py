"""团队日报：团队概览 + 成员摘要 + 协作成果 + 风险与阻塞。"""

from __future__ import annotations

from datetime import date

from app.services.reports.types import GeneratedReport


class TeamReportGenerator:
    def generate(
        self, *, report_date: date, personal_reports: list[GeneratedReport]
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
        if ordered:
            member_lines = "\n".join(
                f"- {report.member_name or '未知成员'}："
                f"{report.summary.get('commits', 0)} 提交 · "
                f"{report.summary.get('tasks', 0)} 任务 · "
                f"{report.summary.get('messages', 0)} 消息"
                for report in ordered
            )
        else:
            member_lines = "- 无成员数据"

        if collaboration:
            collab_lines = "\n".join(
                f"- [{key[0]}] {key[2]}（{key[3]}）：{'、'.join(sorted(names))}"
                for key, names in sorted(collaboration.items())
            )
        else:
            collab_lines = "- 无"

        content = (
            f"# 团队日报（{report_date.isoformat()}）\n\n"
            "## 团队概览\n"
            f"{chr(10).join(overview_lines)}\n\n"
            "## 成员摘要\n"
            f"{member_lines}\n\n"
            "## 协作成果\n"
            f"{collab_lines}\n\n"
            "## 风险与阻塞\n"
            "- 暂未发现阻塞（可手工补充）\n"
        )
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
