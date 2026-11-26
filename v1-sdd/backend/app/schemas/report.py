"""日报相关请求模型。"""

from datetime import date

from pydantic import BaseModel


class ReportUpdate(BaseModel):
    content_md: str
    editor: str = "member"
    change_note: str | None = None


class GenerateRequest(BaseModel):
    report_date: date
    demo: bool = False
    push: bool = True


class PushRequest(BaseModel):
    channel: str = "console"
    target: str | None = None
