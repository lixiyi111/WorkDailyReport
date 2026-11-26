"""V2-022：个人日报四段式生成。"""

from datetime import date, datetime

from app.services.attribution import AttributedItem
from app.services.collectors.attendance import AttendanceRecord
from app.services.reports.personal import PersonalReportGenerator

REPORT_DATE = date(2026, 11, 6)


def _item(
    source_type: str,
    source_id: str,
    title: str,
    role: str,
    occurred_at: datetime | None = None,
) -> AttributedItem:
    return AttributedItem(
        member_id=1,
        category=source_type,
        title=title,
        source_type=source_type,
        source_id=source_id,
        attribution_role=role,
        occurred_at=occurred_at,
    )


ITEMS = [
    _item("commit", "sha-1", "修复登录接口", "author", datetime(2026, 11, 6, 2, 0)),
    _item("task", "task-1", "完成登录联调", "owner"),
    _item("task", "task-1", "协助接口联调", "participant"),
    _item("message", "msg-1", "同步联调结果", "participant"),
]


def test_personal_report_sections() -> None:
    report = PersonalReportGenerator().generate(
        member_id=1, member_name="王芳", report_date=REPORT_DATE, items=ITEMS
    )

    assert "王芳" in report.content_md
    assert "2026-11-06" in report.content_md

    today = report.content_md.split("## 今日完成")[1].split("## 协作贡献")[0]
    assert "修复登录接口" in today
    assert "完成登录联调" in today
    assert "协助接口联调" not in today

    collab = report.content_md.split("## 协作贡献")[1].split("## 问题与阻塞")[0]
    assert "协助接口联调" in collab
    assert "同步联调结果" in collab

    assert "## 问题与阻塞" in report.content_md
    assert "## 明日计划" in report.content_md
    assert report.summary == {
        "commits": 1,
        "tasks": 1,
        "messages": 1,
        "total": 4,
    }


def test_no_data_outputs_no_output() -> None:
    report = PersonalReportGenerator().generate(
        member_id=9, member_name="李四", report_date=REPORT_DATE, items=[]
    )

    assert "## 今日完成" in report.content_md
    assert "无产出" in report.content_md
    assert "无产出" in report.content_md.split("## 今日完成")[1].split("## 协作贡献")[0]
    assert report.summary["total"] == 0


def test_personal_report_is_deterministic() -> None:
    generator = PersonalReportGenerator()
    first = generator.generate(
        member_id=1, member_name="王芳", report_date=REPORT_DATE, items=ITEMS
    )
    second = generator.generate(
        member_id=1, member_name="王芳", report_date=REPORT_DATE, items=ITEMS
    )
    assert first.content_md == second.content_md


def test_personal_report_contains_attendance() -> None:
    attendance = AttendanceRecord(
        member_external_id="ou_1",
        attendance_date=REPORT_DATE,
        status="late",
        check_in_at=datetime(2026, 11, 6, 1, 30),
        check_out_at=datetime(2026, 11, 6, 10, 30),
    )
    report = PersonalReportGenerator().generate(
        member_id=1,
        member_name="王芳",
        report_date=REPORT_DATE,
        items=ITEMS,
        attendance=attendance,
    )

    assert "## 考勤" in report.content_md
    assert "状态：迟到" in report.content_md
    assert "上班：09:30" in report.content_md
    assert "下班：18:30" in report.content_md


def test_personal_report_without_attendance() -> None:
    report = PersonalReportGenerator().generate(
        member_id=1, member_name="王芳", report_date=REPORT_DATE, items=ITEMS
    )
    assert "## 考勤" in report.content_md
    assert "无考勤记录" in report.content_md
