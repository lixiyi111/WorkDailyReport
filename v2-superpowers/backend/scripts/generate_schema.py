"""根据 ORM 元数据生成 MySQL 建表脚本。

运行：`python -m scripts.generate_schema`
输出：`sql/schema.sql`（UTF-8）
"""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_mock_engine
from sqlalchemy.schema import CreateTable

from app.models.entities import Base


def main() -> None:
    engine = create_mock_engine(
        "mysql+aiomysql://root@127.0.0.1:3305/daily_report_v2",
        lambda sql, *args, **kwargs: None,
    )
    lines = [
        "-- v2 智能日报生成器 · MySQL 建表脚本（由 ORM 元数据生成）",
        "-- 使用：mysql -h 127.0.0.1 -P 3305 -u root -p < sql/schema.sql",
        "",
        "CREATE DATABASE IF NOT EXISTS daily_report_v2",
        "  DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
        "USE daily_report_v2;",
        "",
    ]
    for table in Base.metadata.sorted_tables:
        ddl = str(CreateTable(table).compile(dialect=engine.dialect)).strip()
        ddl = ddl.replace("CREATE TABLE ", "CREATE TABLE IF NOT EXISTS ", 1)
        lines.extend([ddl + ";", ""])

    output = Path(__file__).resolve().parents[1] / "sql" / "schema.sql"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"written: {output}")


if __name__ == "__main__":
    main()
