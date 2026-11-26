"""日报相关请求模型。"""

from datetime import date

from pydantic import BaseModel, Field


class ReportEditIn(BaseModel):
    content_md: str = Field(min_length=1)
    editor: str = "web"
    change_note: str | None = None


class GenerateIn(BaseModel):
    report_date: date
    push: bool = False


class PushIn(BaseModel):
    channel: str = "email"  # email / feishu / console / all
