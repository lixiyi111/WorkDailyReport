"""生成层单元测试。"""

from datetime import date

from app.models import Member
from app.services.attribution import AttributedItem
from app.services.reports.personal import PersonalReportGenerator
from app.services.reports.team import TeamReportGenerator


def make_member(name: str = "Alice") -> Member:
    return Member(name=name, email=f"{name.lower()}@example.com")


def test_personal_no_output() -> None:
    generated = PersonalReportGenerator().generate(make_member(), date(2026, 11, 25), [], [])
    assert "无产出" in generated.content_md
    assert generated.summary["no_output"] is True


def test_personal_sections() -> None:
    items = [
        AttributedItem(1, "commit", "feat: 实现日报", "demo/repo@abc1234", "commit", "abc", "author"),
        AttributedItem(1, "message", "群消息", "帮忙 review 了接口", "message", "m1", "participant"),
    ]
    generated = PersonalReportGenerator().generate(
        make_member(), date(2026, 11, 25), items, ["联调飞书接口"]
    )
    assert "今日完成" in generated.content_md
    assert "协作贡献" in generated.content_md
    assert "联调飞书接口" in generated.content_md
    assert generated.summary["commits"] == 1
    assert generated.summary["messages"] == 1


def test_team_report() -> None:
    member = make_member()
    personal = PersonalReportGenerator().generate(member, date(2026, 11, 25), [], [])
    item = AttributedItem(1, "message", "群消息", "hi", "message", "m1", "participant")
    generated = TeamReportGenerator().generate(
        date(2026, 11, 25), [(member, personal)], [(member, item)], ["Alice 当天无产出"]
    )
    assert "团队概览" in generated.content_md
    assert "成员摘要" in generated.content_md
    assert "Alice" in generated.content_md
    assert "Alice 当天无产出" in generated.content_md
