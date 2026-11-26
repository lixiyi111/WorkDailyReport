"""成员与身份绑定请求模型。"""

from pydantic import BaseModel


class MemberCreate(BaseModel):
    name: str
    email: str
    role: str = "member"


class IdentityBind(BaseModel):
    provider: str
    external_id: str
    external_username: str | None = None
    verified: bool = False
