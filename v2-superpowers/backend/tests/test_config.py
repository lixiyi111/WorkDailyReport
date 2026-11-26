"""V2-001：配置默认值与数据库连接串。"""

from app.core.config import Settings


def test_default_db_is_v2_database() -> None:
    """v2 默认连接独立库 daily_report_v2 / 端口 3305，避免覆盖 v1 数据。"""
    settings = Settings(_env_file=None)
    assert settings.db_port == 3305
    assert settings.db_name == "daily_report_v2"


def test_database_url_uses_mysql_aiomysql() -> None:
    """数据库连接串必须是 SQLAlchemy 异步 MySQL 驱动。"""
    settings = Settings(_env_file=None)
    assert settings.database_url.startswith("mysql+aiomysql://")
