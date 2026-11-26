"""数据库声明基类。"""

from sqlalchemy import BigInteger, Integer
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """所有 ORM 模型的基类。"""


# MySQL 用 BIGINT，SQLite 测试时退化为 INTEGER 以支持自增主键
BIGINT_PK = BigInteger().with_variant(Integer, "sqlite")
