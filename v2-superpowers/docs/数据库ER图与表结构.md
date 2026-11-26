# v2 数据库 ER 图与表结构

> 数据库：`daily_report_v2` @ `127.0.0.1:3305`
> 建表脚本：[../backend/sql/schema.sql](../backend/sql/schema.sql)
> 表数量：**14 张**
> 说明：ER 图只画**表名（中英文）与关系**，不画字段；字段详情见第 2 节。
> v2 的 DDL 由 SQLAlchemy ORM 生成，类型多用 `VARCHAR`；`role`、`status` 等默认值由应用层提供。

## 1. ER 图

### 1.1 成员与权限

```mermaid
erDiagram
  members["members 成员"]
  member_identities["member_identities 成员身份"]
  app_users["app_users 登录账号"]

  members ||--o{ member_identities : "1:N"
  members |o--o{ app_users : "绑定"
```

### 1.2 采集与原始数据

```mermaid
erDiagram
  members["members 成员"]
  member_identities["member_identities 成员身份"]
  repositories["repositories 仓库"]
  raw_commits["raw_commits 原始提交"]
  raw_tasks["raw_tasks 原始任务"]
  raw_messages["raw_messages 原始消息"]
  identity_unmatched["identity_unmatched 未归属身份"]

  repositories ||--o{ raw_commits : "1:N"
  member_identities |o--o{ raw_commits : "author"
  member_identities |o--o{ raw_tasks : "owner"
  member_identities |o--o{ raw_messages : "sender"
  members |o--o{ identity_unmatched : "resolved"
```

### 1.3 日报与推送

```mermaid
erDiagram
  members["members 成员"]
  daily_reports["daily_reports 日报"]
  report_items["report_items 日报条目"]
  report_versions["report_versions 日报版本"]
  push_logs["push_logs 推送记录"]

  members |o--o{ daily_reports : "1:N"
  daily_reports ||--o{ report_items : "1:N"
  daily_reports ||--o{ report_versions : "1:N"
  daily_reports ||--o{ push_logs : "1:N"
```

### 1.4 考勤

```mermaid
erDiagram
  members["members 成员"]
  attendance_records["attendance_records 考勤记录"]

  members ||--o{ attendance_records : "1:N"
```

### 1.5 数据源同步状态

```mermaid
erDiagram
  source_sync_state["source_sync_state 同步状态"]
```

## 2. 表结构详情

### 2.1 成员与权限

#### members 成员

| 字段 | 类型 | 约束 / 默认 | 说明 |
|------|------|-------------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| name | VARCHAR(64) | NOT NULL | 姓名 |
| email | VARCHAR(255) | NOT NULL, UNIQUE | 邮箱，唯一 |
| role | VARCHAR(16) | NOT NULL；应用默认 `member` | member / leader / mentor |
| status | VARCHAR(16) | NOT NULL；应用默认 `active` | active / inactive |
| created_at | DATETIME | NOT NULL；应用层写入 UTC | 创建时间 |
| updated_at | DATETIME | NOT NULL；应用层更新 | 更新时间 |

索引：`uk_members_email(email)`。

#### member_identities 成员身份

| 字段 | 类型 | 约束 / 默认 | 说明 |
|------|------|-------------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| member_id | BIGINT | NOT NULL, FK → members.id | 所属成员 |
| provider | VARCHAR(16) | NOT NULL | github / feishu |
| external_id | VARCHAR(128) | NOT NULL | 平台内唯一 ID |
| external_username | VARCHAR(128) | NULL | 平台用户名 |
| verified | BOOL | NOT NULL；应用默认 `false` | 是否人工确认 |
| created_at | DATETIME | NOT NULL；应用层写入 UTC | 创建时间 |

索引：`uk_provider_external(provider, external_id)`、`idx_identity_member(member_id)`。

#### app_users 登录账号

| 字段 | 类型 | 约束 / 默认 | 说明 |
|------|------|-------------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| username | VARCHAR(64) | NOT NULL, UNIQUE | 登录名 |
| password_hash | VARCHAR(255) | NOT NULL | PBKDF2 哈希 |
| role | VARCHAR(16) | NOT NULL；应用默认 `member` | admin / leader / member |
| member_id | BIGINT | NULL, FK → members.id | 绑定的成员 |
| active | BOOL | NOT NULL；应用默认 `true` | 是否启用 |
| created_at | DATETIME | NOT NULL；应用层写入 UTC | 创建时间 |
| updated_at | DATETIME | NOT NULL；应用层更新 | 更新时间 |

索引：`uk_app_users_username(username)`。

### 2.2 采集与原始数据

#### repositories 仓库

| 字段 | 类型 | 约束 / 默认 | 说明 |
|------|------|-------------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| owner | VARCHAR(128) | NOT NULL | 仓库 owner |
| name | VARCHAR(128) | NOT NULL | 仓库名 |
| default_branch | VARCHAR(128) | NOT NULL；应用默认 `main` | 默认分支 |
| enabled | BOOL | NOT NULL；应用默认 `true` | 是否启用采集 |
| created_at | DATETIME | NOT NULL；应用层写入 UTC | 创建时间 |

索引：`uk_repo(owner, name)`。

#### raw_commits 原始提交

| 字段 | 类型 | 约束 / 默认 | 说明 |
|------|------|-------------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| repo_id | BIGINT | NOT NULL, FK → repositories.id | 仓库 |
| sha | VARCHAR(40) | NOT NULL | 提交 SHA |
| author_identity_id | BIGINT | NULL, FK → member_identities.id | 作者身份 |
| author_name | VARCHAR(128) | NOT NULL | 作者名 |
| author_email | VARCHAR(255) | NULL | 作者邮箱 |
| committed_at | DATETIME | NOT NULL | 提交时间 |
| message | TEXT | NOT NULL | 提交说明 |
| branch | VARCHAR(128) | NULL | 分支 |
| url | VARCHAR(512) | NULL | 提交链接 |
| pr_number | INTEGER | NULL | 关联 PR |
| collected_at | DATETIME | NOT NULL；应用层写入 UTC | 采集时间 |

索引：`uk_repo_sha(repo_id, sha)`、`idx_commit_time(committed_at)`、`idx_commit_author(author_identity_id)`。

#### raw_tasks 原始任务

| 字段 | 类型 | 约束 / 默认 | 说明 |
|------|------|-------------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| task_id | VARCHAR(128) | NOT NULL, UNIQUE | 飞书任务 ID |
| title | VARCHAR(512) | NOT NULL | 任务标题 |
| owner_identity_id | BIGINT | NULL, FK → member_identities.id | 负责人身份 |
| participants_json | JSON | NULL | 参与人列表 |
| status | VARCHAR(64) | NOT NULL | 任务状态 |
| status_changed_at | DATETIME | NULL | 状态变更时间 |
| created_at_source | DATETIME | NULL | 源创建时间 |
| updated_at_source | DATETIME | NULL | 源更新时间 |
| collected_at | DATETIME | NOT NULL；应用层写入 UTC | 采集时间 |

索引：`uk_task_id(task_id)`、`idx_task_owner(owner_identity_id)`、`idx_task_time(status_changed_at)`。

#### raw_messages 原始消息

| 字段 | 类型 | 约束 / 默认 | 说明 |
|------|------|-------------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| message_id | VARCHAR(128) | NOT NULL, UNIQUE | 飞书消息 ID |
| chat_id | VARCHAR(128) | NOT NULL | 群 ID |
| sender_identity_id | BIGINT | NULL, FK → member_identities.id | 发送人身份 |
| sender_name | VARCHAR(128) | NULL | 发送人名称 |
| sent_at | DATETIME | NOT NULL | 发送时间 |
| content_excerpt | TEXT | NULL | 截断后的摘要 |
| content_hash | VARCHAR(64) | NULL | 内容哈希 |
| collected_at | DATETIME | NOT NULL；应用层写入 UTC | 采集时间 |

索引：`uk_message_id(message_id)`、`idx_chat_sent(chat_id, sent_at)`、`idx_message_sender(sender_identity_id)`。

#### identity_unmatched 未归属身份

| 字段 | 类型 | 约束 / 默认 | 说明 |
|------|------|-------------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| provider | VARCHAR(16) | NOT NULL | github / feishu |
| external_id | VARCHAR(128) | NOT NULL | 平台内 ID |
| external_name | VARCHAR(128) | NULL | 平台内名称 |
| source_type | VARCHAR(32) | NOT NULL | commit / task / message / attendance |
| source_id | VARCHAR(128) | NOT NULL | 来源记录 ID |
| resolved_member_id | BIGINT | NULL, FK → members.id | 人工绑定后的成员 |
| resolved_at | DATETIME | NULL | 绑定时间 |
| created_at | DATETIME | NOT NULL；应用层写入 UTC | 创建时间 |

索引：`uk_unmatched(provider, external_id, source_type, source_id)`。

### 2.3 日报与推送

#### daily_reports 日报

| 字段 | 类型 | 约束 / 默认 | 说明 |
|------|------|-------------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| report_date | DATE | NOT NULL | 日报日期 |
| report_type | VARCHAR(16) | NOT NULL | personal / team |
| scope_key | VARCHAR(64) | NOT NULL | 个人 `member:{id}`，团队 `team` |
| member_id | BIGINT | NULL, FK → members.id | 个人日报成员 |
| status | VARCHAR(16) | NOT NULL；应用默认 `generated` | draft / generated / published |
| current_version | INTEGER | NOT NULL；应用默认 1 | 当前版本 |
| content_md | MEDIUMTEXT | NOT NULL | Markdown 正文 |
| summary_json | JSON | NULL | 统计摘要 |
| generated_at | DATETIME | NOT NULL；应用层写入 UTC | 生成时间 |
| updated_at | DATETIME | NOT NULL；应用层更新 | 更新时间 |

索引：`uk_report_scope(report_date, report_type, scope_key)`、`idx_report_date(report_date)`、`idx_report_member(member_id)`。

#### report_items 日报条目

| 字段 | 类型 | 约束 / 默认 | 说明 |
|------|------|-------------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| report_id | BIGINT | NOT NULL, FK → daily_reports.id, ON DELETE CASCADE | 日报 |
| category | VARCHAR(32) | NOT NULL | commit / task / message / collaboration / manual |
| title | VARCHAR(512) | NOT NULL | 条目标题 |
| detail | TEXT | NULL | 详情 |
| source_type | VARCHAR(32) | NULL | 原始数据类型 |
| source_id | VARCHAR(128) | NULL | 原始数据 ID |
| attribution_role | VARCHAR(32) | NULL | author / reviewer / assignee / participant / owner |
| sort_order | INTEGER | NOT NULL；应用默认 0 | 排序 |
| created_at | DATETIME | NOT NULL；应用层写入 UTC | 创建时间 |

索引：`idx_item_report(report_id)`、`idx_item_source(source_type, source_id)`。

#### report_versions 日报版本

| 字段 | 类型 | 约束 / 默认 | 说明 |
|------|------|-------------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| report_id | BIGINT | NOT NULL, FK → daily_reports.id, ON DELETE CASCADE | 日报 |
| version | INTEGER | NOT NULL | 版本号 |
| content_md | MEDIUMTEXT | NOT NULL | 该版本正文 |
| editor | VARCHAR(64) | NOT NULL | 编辑者 |
| change_note | VARCHAR(255) | NULL | 变更说明 |
| created_at | DATETIME | NOT NULL；应用层写入 UTC | 创建时间 |

索引：`uk_report_version(report_id, version)`。

#### push_logs 推送记录

| 字段 | 类型 | 约束 / 默认 | 说明 |
|------|------|-------------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| report_id | BIGINT | NOT NULL, FK → daily_reports.id, ON DELETE CASCADE | 日报 |
| channel | VARCHAR(16) | NOT NULL | email / feishu / console |
| target | VARCHAR(255) | NOT NULL | 目标 |
| status | VARCHAR(16) | NOT NULL | success / failed |
| attempt | INTEGER | NOT NULL；应用默认 1 | 第几次尝试 |
| error_message | VARCHAR(1024) | NULL | 错误信息 |
| sent_at | DATETIME | NOT NULL；应用层写入 UTC | 发送时间 |

索引：`idx_push_report(report_id)`、`idx_push_status(status, sent_at)`。

### 2.4 考勤

#### attendance_records 考勤记录

| 字段 | 类型 | 约束 / 默认 | 说明 |
|------|------|-------------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| member_id | BIGINT | NOT NULL, FK → members.id | 成员 |
| attendance_date | DATE | NOT NULL | 考勤日期 |
| status | VARCHAR(16) | NOT NULL | normal / late / early / absent / leave / holiday |
| check_in_at | DATETIME | NULL | 最早上班时间（UTC） |
| check_out_at | DATETIME | NULL | 最晚下班时间（UTC） |
| source | VARCHAR(32) | NOT NULL；应用默认 `feishu` | feishu / mock |
| source_id | VARCHAR(128) | NULL | 来源记录 ID |
| created_at | DATETIME | NOT NULL；应用层写入 UTC | 创建时间 |
| updated_at | DATETIME | NOT NULL；应用层更新 | 更新时间 |

索引：`uk_attendance_member_date(member_id, attendance_date)`、`idx_attendance_date(attendance_date)`。

### 2.5 数据源同步状态

#### source_sync_state 同步状态

| 字段 | 类型 | 约束 / 默认 | 说明 |
|------|------|-------------|------|
| id | BIGINT | PK, AUTO_INCREMENT | 主键 |
| source | VARCHAR(32) | NOT NULL | github / feishu_tasks / feishu_messages / feishu_attendance |
| resource_key | VARCHAR(191) | NOT NULL | 资源标识（日报日期） |
| last_cursor | VARCHAR(255) | NULL | 增量游标 |
| last_synced_at | DATETIME | NULL | 最近同步时间 |
| status | VARCHAR(16) | NOT NULL；应用默认 `idle` | idle / success / partial / failed |
| error_message | VARCHAR(1024) | NULL | 错误信息 |
| updated_at | DATETIME | NOT NULL；应用层更新 | 更新时间 |

索引：`uk_source_resource(source, resource_key)`。

## 3. v1 / v2 表结构差异

| 差异 | v1 | v2 |
|------|----|----|
| 表数量 | 17 张 | 14 张 |
| v2 没有的表 | `collection_runs`、`data_sources`、`system_settings` | — |
| 考勤表字段 | `work_date`、`check_in`、`check_out`、`late_minutes`、`early_minutes`、`raw_json` | `attendance_date`、`check_in_at`、`check_out_at`、`source`、`source_id` |
| 枚举 | MySQL `ENUM` | `VARCHAR` + 应用层校验 |
| 主键类型 | `BIGINT UNSIGNED` | `BIGINT`（SQLite 测试库自动降级为 `INTEGER`） |
| 默认值 | 多数在 DDL 中 | 多数由 ORM / 应用层提供 |
| 建表方式 | 手写 SQL | SQLAlchemy ORM 生成 `schema.sql` |
| 数据库 | `daily_report` | `daily_report_v2`（独立库，不覆盖 v1） |
