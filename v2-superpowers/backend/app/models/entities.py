"""v2 数据模型：14 张核心表，字段与约束按 v2 设计输入重新落地。

设计要点：
- 主键用 BigInteger，SQLite 测试库自动降级为 Integer；
- 原始数据表靠自然键唯一约束保证幂等；
- 日报唯一键带 scope_key，避免团队日报 member_id 为 NULL 时唯一键失效；
- 时间统一存 UTC（naive），由 core.timeutil 负责窗口换算。
"""

from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

ID_TYPE = BigInteger().with_variant(Integer, "sqlite")
LONG_TEXT = Text().with_variant(MEDIUMTEXT(), "mysql")


def utcnow() -> datetime:
    """返回不带时区的 UTC 时间，便于 MySQL DATETIME 存储。"""
    return datetime.now(UTC).replace(tzinfo=None)


class Base(DeclarativeBase):
    """所有 ORM 实体的声明基类。"""


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False, default="member")
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, onupdate=utcnow
    )

    __table_args__ = (UniqueConstraint("email", name="uk_members_email"),)


class MemberIdentity(Base):
    __tablename__ = "member_identities"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    member_id: Mapped[int] = mapped_column(
        ID_TYPE, ForeignKey("members.id"), nullable=False
    )
    provider: Mapped[str] = mapped_column(String(16), nullable=False)
    external_id: Mapped[str] = mapped_column(String(128), nullable=False)
    external_username: Mapped[str | None] = mapped_column(String(128), nullable=True)
    verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)

    __table_args__ = (
        UniqueConstraint("provider", "external_id", name="uk_provider_external"),
        Index("idx_identity_member", "member_id"),
    )


class Repository(Base):
    __tablename__ = "repositories"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    owner: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    default_branch: Mapped[str] = mapped_column(
        String(128), nullable=False, default="main"
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)

    __table_args__ = (UniqueConstraint("owner", "name", name="uk_repo"),)


class RawCommit(Base):
    __tablename__ = "raw_commits"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    repo_id: Mapped[int] = mapped_column(
        ID_TYPE, ForeignKey("repositories.id"), nullable=False
    )
    sha: Mapped[str] = mapped_column(String(40), nullable=False)
    author_identity_id: Mapped[int | None] = mapped_column(
        ID_TYPE, ForeignKey("member_identities.id"), nullable=True
    )
    author_name: Mapped[str] = mapped_column(String(128), nullable=False)
    author_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    committed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    branch: Mapped[str | None] = mapped_column(String(128), nullable=True)
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    pr_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)

    __table_args__ = (
        UniqueConstraint("repo_id", "sha", name="uk_repo_sha"),
        Index("idx_commit_time", "committed_at"),
        Index("idx_commit_author", "author_identity_id"),
    )


class RawTask(Base):
    __tablename__ = "raw_tasks"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    task_id: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    owner_identity_id: Mapped[int | None] = mapped_column(
        ID_TYPE, ForeignKey("member_identities.id"), nullable=True
    )
    participants_json: Mapped[list | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False)
    status_changed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at_source: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at_source: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)

    __table_args__ = (
        UniqueConstraint("task_id", name="uk_task_id"),
        Index("idx_task_owner", "owner_identity_id"),
        Index("idx_task_time", "status_changed_at"),
    )


class RawMessage(Base):
    __tablename__ = "raw_messages"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    message_id: Mapped[str] = mapped_column(String(128), nullable=False)
    chat_id: Mapped[str] = mapped_column(String(128), nullable=False)
    sender_identity_id: Mapped[int | None] = mapped_column(
        ID_TYPE, ForeignKey("member_identities.id"), nullable=True
    )
    sender_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    content_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    collected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)

    __table_args__ = (
        UniqueConstraint("message_id", name="uk_message_id"),
        Index("idx_chat_sent", "chat_id", "sent_at"),
        Index("idx_message_sender", "sender_identity_id"),
    )


class IdentityUnmatched(Base):
    __tablename__ = "identity_unmatched"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(String(16), nullable=False)
    external_id: Mapped[str] = mapped_column(String(128), nullable=False)
    external_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_id: Mapped[str] = mapped_column(String(128), nullable=False)
    resolved_member_id: Mapped[int | None] = mapped_column(
        ID_TYPE, ForeignKey("members.id"), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "external_id",
            "source_type",
            "source_id",
            name="uk_unmatched",
        ),
    )


class DailyReport(Base):
    __tablename__ = "daily_reports"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    report_date: Mapped[date] = mapped_column(Date, nullable=False)
    report_type: Mapped[str] = mapped_column(String(16), nullable=False)
    scope_key: Mapped[str] = mapped_column(String(64), nullable=False)
    member_id: Mapped[int | None] = mapped_column(
        ID_TYPE, ForeignKey("members.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="generated")
    current_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    content_md: Mapped[str] = mapped_column(LONG_TEXT, nullable=False)
    summary_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, onupdate=utcnow
    )

    __table_args__ = (
        UniqueConstraint(
            "report_date", "report_type", "scope_key", name="uk_report_scope"
        ),
        Index("idx_report_date", "report_date"),
        Index("idx_report_member", "member_id"),
    )


class ReportItem(Base):
    __tablename__ = "report_items"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    report_id: Mapped[int] = mapped_column(
        ID_TYPE, ForeignKey("daily_reports.id", ondelete="CASCADE"), nullable=False
    )
    category: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    source_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    attribution_role: Mapped[str | None] = mapped_column(String(32), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)

    __table_args__ = (
        Index("idx_item_report", "report_id"),
        Index("idx_item_source", "source_type", "source_id"),
    )


class ReportVersion(Base):
    __tablename__ = "report_versions"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    report_id: Mapped[int] = mapped_column(
        ID_TYPE, ForeignKey("daily_reports.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    content_md: Mapped[str] = mapped_column(LONG_TEXT, nullable=False)
    editor: Mapped[str] = mapped_column(String(64), nullable=False)
    change_note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)

    __table_args__ = (
        UniqueConstraint("report_id", "version", name="uk_report_version"),
    )


class PushLog(Base):
    __tablename__ = "push_logs"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    report_id: Mapped[int] = mapped_column(
        ID_TYPE, ForeignKey("daily_reports.id", ondelete="CASCADE"), nullable=False
    )
    channel: Mapped[str] = mapped_column(String(16), nullable=False)
    target: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    attempt: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    error_message: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)

    __table_args__ = (
        Index("idx_push_report", "report_id"),
        Index("idx_push_status", "status", "sent_at"),
    )


class SourceSyncState(Base):
    __tablename__ = "source_sync_state"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    resource_key: Mapped[str] = mapped_column(String(191), nullable=False)
    last_cursor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="idle")
    error_message: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, onupdate=utcnow
    )

    __table_args__ = (
        UniqueConstraint("source", "resource_key", name="uk_source_resource"),
    )


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    member_id: Mapped[int] = mapped_column(
        ID_TYPE, ForeignKey("members.id"), nullable=False
    )
    attendance_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    check_in_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    check_out_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="feishu")
    source_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, onupdate=utcnow
    )

    __table_args__ = (
        UniqueConstraint(
            "member_id", "attendance_date", name="uk_attendance_member_date"
        ),
        Index("idx_attendance_date", "attendance_date"),
    )


class AppUser(Base):
    __tablename__ = "app_users"

    id: Mapped[int] = mapped_column(ID_TYPE, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False, default="member")
    member_id: Mapped[int | None] = mapped_column(
        ID_TYPE, ForeignKey("members.id"), nullable=True
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=utcnow, onupdate=utcnow
    )

    __table_args__ = (UniqueConstraint("username", name="uk_app_users_username"),)
