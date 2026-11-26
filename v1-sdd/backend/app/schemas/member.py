"""成员与身份绑定请求模型。"""

from typing import Literal

from pydantic import BaseModel, EmailStr


class MemberCreate(BaseModel):
    name: str
    email: EmailStr
    role: Literal["member", "leader", "mentor"] = "member"


class MemberUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    role: Literal["member", "leader", "mentor"] | None = None
    status: Literal["active", "inactive"] | None = None


class IdentityBind(BaseModel):
    provider: Literal["github", "feishu"]
    external_id: str
    external_username: str | None = None
    verified: bool = False
