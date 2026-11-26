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
    app_name: str = "智能日报生成器 v1 (SDD)"
    app_env: str = "development"
    api_prefix: str = "/api"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # GitHub 数据源（只读个人访问令牌）
    github_token: str = ""
    github_api_base: str = "https://api.github.com"

    # 飞书开放平台（自建应用）
    feishu_app_id: str = ""
    feishu_app_secret: str = ""
    feishu_base_url: str = "https://open.feishu.cn"

    # 邮件推送（SMTP）
    smtp_host: str = "smtp.qq.com"
    smtp_port: int = 465
    smtp_user: str = ""
    smtp_auth_code: str = ""
    smtp_from_name: str = "智能日报"

    # 存储（MySQL）
    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "daily_report"
    db_charset: str = "utf8mb4"

    # 可选：完整 SQLAlchemy URL（测试/演示可用 SQLite），为空时由 DB_* 拼接
    database_url: str = ""

    # 数据源与推送配置
    github_repos: str = ""          # 逗号分隔：owner/repo
    feishu_chat_ids: str = ""       # 逗号分隔的 chat_id
    report_recipients: str = ""     # 逗号分隔的收件邮箱
    feishu_report_chat_id: str = ""

    # 运行开关
    auto_create_tables: bool = True
    enable_scheduler: bool = False
    report_push_time: str = "09:00"

    @property
    def cors_origin_list(self) -> list[str]:
        """把逗号分隔的 CORS 来源解析为列表。"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def sqlalchemy_url(self) -> str:
        """返回 SQLAlchemy 连接串：优先 database_url，否则由 DB_* 拼接。"""
        if self.database_url:
            return self.database_url
        user = quote_plus(self.db_user)
        password = quote_plus(self.db_password)
        return (
            f"mysql+aiomysql://{user}:{password}@{self.db_host}:{self.db_port}/"
            f"{self.db_name}?charset={self.db_charset}"
        )

    @property
    def github_repo_list(self) -> list[str]:
        return [r.strip() for r in self.github_repos.split(",") if r.strip()]

    @property
    def feishu_chat_id_list(self) -> list[str]:
        return [c.strip() for c in self.feishu_chat_ids.split(",") if c.strip()]

    @property
    def report_recipient_list(self) -> list[str]:
        return [e.strip() for e in self.report_recipients.split(",") if e.strip()]


@lru_cache
def get_settings() -> Settings:
    """返回进程内缓存的配置单例。"""
    return Settings()
