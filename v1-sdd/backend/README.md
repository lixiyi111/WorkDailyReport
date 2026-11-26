# 智能日报生成器 · v1（SDD）后端

FastAPI + SQLAlchemy 实现的智能日报后端：采集 GitHub 提交、飞书任务与群消息，生成个人 / 团队日报，经邮件、飞书机器人或控制台推送。

## 已实现

- **采集层**：GitHub（httpx）、飞书任务、飞书群消息、Mock 数据源；
- **生成层**：成员身份解析、协作归属、个人日报、团队日报；
- **推送层**：SMTP 邮件、飞书机器人、控制台；
- **编排**：自然键 upsert、幂等重跑、数据源降级、未归属记录；
- **API**：日报查询 / 详情 / 编辑 / 生成 / 推送、成员与身份绑定、推送日志；
- **调度**：APScheduler 次日 09:00 生成前一自然日日报（可选开启）。

## 目录

```
backend/
├── app/
│   ├── main.py                 # 应用入口
│   ├── core/                   # 配置、日志、时间窗口、重试
│   ├── db/                     # 声明基类与异步会话
│   ├── models/                 # 12 张表的 ORM 模型
│   ├── schemas/                # 请求模型
│   ├── services/
│   │   ├── collectors/         # GitHub / 飞书 / Mock 采集
│   │   ├── reports/            # 个人 / 团队日报生成
│   │   ├── pushers/            # 邮件 / 飞书 / 控制台推送
│   │   ├── identity.py         # 身份解析
│   │   ├── attribution.py      # 协作归属
│   │   ├── orchestrator.py     # 主编排
│   │   └── factory.py          # 依赖装配
│   ├── api/routes/             # REST 接口
│   ├── scheduler.py            # 定时任务
│   └── services/demo.py        # 演示数据
├── scripts/
│   ├── init_db.py              # 初始化 MySQL 表
│   └── demo.py                 # SQLite + Mock 演示
├── tests/
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```

## 运行

### 1. 配置

```bash
cp .env.example .env    # 填入 GITHUB_TOKEN / 飞书 / SMTP / DB_PASSWORD
```

### 2. 创建数据库与表（使用 SQL 文件）

```bash
mysql -h 127.0.0.1 -P 3305 -u root -p < sql/schema.sql
```

`sql/schema.sql` 会创建 `daily_report` 库与 12 张表。`.env` 中 `AUTO_CREATE_TABLES=false`，应用启动不会自动建表。

### 3. 安装依赖

```bash
conda activate work_daily
pip install -r requirements-dev.txt
```

### 4. 启动

```bash
uvicorn app.main:app --reload --port 8000
```

接口文档：http://127.0.0.1:8000/docs

## 本地演示（无需外部凭证）

```bash
python -m scripts.demo
```

使用 SQLite + Mock 数据跑通「采集 → 生成 → 推送」，并在控制台输出团队日报。

## 测试与静态检查

```bash
pytest -q
ruff check .
```

## 主要 API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查（只返回凭证是否就绪） |
| GET | `/api/reports?date=&type=&member_id=` | 查询日报列表 |
| GET | `/api/reports/{id}` | 日报详情与条目 |
| PUT | `/api/reports/{id}` | 编辑日报（生成新版本） |
| POST | `/api/reports/generate` | 生成日报（`demo=true` 用 Mock） |
| POST | `/api/reports/{id}/push` | 推送日报 |
| GET/POST | `/api/members` | 成员列表 / 新建 |
| POST | `/api/members/{id}/identities` | 绑定身份 |
| GET | `/api/identities/unmatched` | 未归属记录 |
| GET | `/api/sources/status` | 数据源状态 |
| GET | `/api/push-logs` | 推送日志 |

## 说明

- 真实 GitHub / 飞书 / 邮件需要凭证就绪；当前状态见 [../../PROJECT.md](../../PROJECT.md)。
- `.env` 已被 git 忽略，只提交 `.env.example`。
- Vue 前端仍为骨架，尚未接入日报接口；v1 的 Web 编辑能力目前通过 API 提供。
