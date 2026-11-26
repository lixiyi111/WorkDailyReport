"""成员与身份相关请求模型。"""

from pydantic import BaseModel, Field


class IdentityBindIn(BaseModel):
    provider: str = Field(pattern="^(github|feishu)$")
    external_id: str = Field(min_length=1)
    external_username: str | None = None
