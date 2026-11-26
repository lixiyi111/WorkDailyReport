"""V2-023：团队日报四段式与跨成员去重。"""

from datetime import date

from app.services.attribution import AttributedItem
from app.services.reports.personal import PersonalReportGenerator
from app.services.reports.team import TeamReportGenerator

REPORT_DATE = date(2026, 11, 6)


def _collab_item(member_id: int) -> AttributedItem:
    return AttributedItem(
        member_id=member_id,
        category="task",
        title="登录联调",
        source_type="task",
        source_id="task-1",
        attribution_role="participant",
    )


def _personal(member_id: int, name: str):
    return PersonalReportGenerator().generate(
        member_id=member_id,
        member_name=name,
        report_date=REPORT_DATE,
        items=[_collab_item(member_id)],
    )


def test_team_report_sections() -> None:
    reports = [_personal(1, "王芳"), _personal(2, "李四")]
    team = TeamReportGenerator().generate(
        report_date=REPORT_DATE, personal_reports=reports
    )

    assert "2026-11-06" in team.content_md
    assert "## 团队概览" in team.content_md
    assert "## 成员摘要" in team.content_md
    assert "## 协作成果" in team.content_md
    assert "## 风险与阻塞" in team.content_md
    assert "2 人" in team.content_md
    assert "王芳" in team.content_md
    assert "李四" in team.content_md
    assert team.summary["members"] == 2
    assert team.summary["tasks"] == 2


def test_team_dedup_across_members() -> None:
    reports = [_personal(1, "王芳"), _personal(2, "李四")]
    team = TeamReportGenerator().generate(
        report_date=REPORT_DATE, personal_reports=reports
    )

    collab = team.content_md.split("## 协作成果")[1].split("## 风险与阻塞")[0]
    assert collab.count("登录联调") == 1
    assert "王芳" in collab
    assert "李四" in collab
    assert team.summary["collaboration"] == 1


def test_team_report_without_members() -> None:
    team = TeamReportGenerator().generate(
        report_date=REPORT_DATE, personal_reports=[]
    )
    assert "0 人" in team.content_md
    assert "无成员数据" in team.content_md
    assert team.summary["members"] == 0
