"""应用配置：全部敏感凭证只从环境变量 / .env 读取，不写入代码。"""

from functools import lru_cache
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """集中管理运行配置。

    字段名与 .env 中的键名一一对应（大小写不敏感）：
    例如 ``github_token`` 对应 ``GITHUB_TOKEN``。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 应用基础信息
    app_name: str = "智能日报生成器 v2 (Superpowers)"
    app_env: str = "development"
    api_prefix: str = "/api"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # GitHub 数据源（只读个人访问令牌）
    github_token: str = ""
    github_api_base: str = "https://api.github.com"

    # 飞书开放平台（自建应用）
    feishu_app_id: str = ""
    feishu_app_secret: str = ""

    # 邮件推送（SMTP）
    smtp_host: str = "smtp.qq.com"
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_auth_code: str = ""
    smtp_from_name: str = "智能日报"

    # 存储（MySQL）
    db_host: str = "127.0.0.1"
    db_port: int = 3305
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "daily_report_v2"
    db_charset: str = "utf8mb4"

    @property
    def cors_origin_list(self) -> list[str]:
        """把逗号分隔的 CORS 来源解析为列表。"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def database_url(self) -> str:
        """拼接 SQLAlchemy 异步连接串（mysql + aiomysql）。"""
        user = quote_plus(self.db_user)
        password = quote_plus(self.db_password)
        return (
            f"mysql+aiomysql://{user}:{password}@{self.db_host}:{self.db_port}/"
            f"{self.db_name}?charset={self.db_charset}"
        )


@lru_cache
def get_settings() -> Settings:
    """返回进程内缓存的配置单例。"""
    return Settings()
