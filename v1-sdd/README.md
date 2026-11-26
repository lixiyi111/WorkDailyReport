# 智能日报生成器 · v1（SDD）

FastAPI + Vue 3 + MySQL 实现的团队日报系统：采集 GitHub 提交与飞书任务/消息，生成个人与团队日报，支持邮件、飞书机器人与控制台推送。

## 目录结构

```
v1-sdd/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # health / reports / members / sources
│   │   ├── core/            # 配置、日志、时间窗口、重试
│   │   ├── db/              # 声明基类、异步会话
│   │   ├── models/          # 12 张表的 ORM
│   │   ├── schemas/         # 请求模型
│   │   ├── services/        # 采集 / 生成 / 推送 / 编排
│   │   ├── main.py          # 应用入口
│   │   └── scheduler.py     # 次日 09:00 定时任务
│   ├── scripts/             # init_db.py / demo.py
│   ├── sql/                 # schema.sql / demo_data.sql
│   ├── tests/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/client.js
│   │   ├── router/index.js
│   │   ├── views/           # Home / Reports / ReportDetail
│   │   ├── assets/main.css
│   │   ├── App.vue
│   │   └── main.js
│   ├── package.json
│   └── vite.config.js
├── docs/                    # 需求记录、AI 日志、评审单、验收表、技能笔记、数据库 ER 图
└── specs/                   # proposal / design / tasks + uml
```

## 运行

### 1. 环境

- conda 环境 `work_daily`（Python 3.12）
- MySQL 8，本项目默认 `127.0.0.1:3305`
- Node.js 20+

### 2. 数据库

```bash
cd v1-sdd/backend
mysql -h 127.0.0.1 -P 3305 -u root -p daily_report < sql/schema.sql
# 可选：导入演示数据（会先清空业务表）
mysql -h 127.0.0.1 -P 3305 -u root -p daily_report < sql/demo_data.sql
```

### 3. 后端

```bash
conda activate work_daily
cd v1-sdd/backend
pip install -r requirements-dev.txt
cp .env.example .env      # 填入凭证；数据库默认 3305
uvicorn app.main:app --reload --port 8000
```

> **必须在 `work_daily` 环境运行。** `base` 环境是 Python 3.9，会出现
> `TypeError: unsupported operand type(s) for |`；本项目要求 Python 3.12+。

- API 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/health

### 4. 前端

```bash
cd v1-sdd/frontend
npm install
npm run dev
```

访问 http://localhost:5173：

- `/` 工作台
- `/sources` 数据源配置、连接测试、手动采集
- `/records` 工作数据（提交 / 任务 / 消息）
- `/reports` 日报列表
- `/reports/:id` 日报详情 / 编辑 / 推送
- `/members` 成员管理与身份绑定
- `/push` 推送记录
- `/runs` 运行日志
- `/attendance` 考勤（当前 Mock）
- `/settings` 系统设置

## 登录与权限

首次启动会按 `.env` 中的 `AUTH_*` 自动创建演示账号：

| 角色 | 能做什么 |
|------|----------|
| **admin** | 全部功能，含系统设置与账号管理 |
| **leader** | 数据源、工作数据、日报生成/编辑/推送、成员、推送、运行日志、考勤 |
| **member** | 工作台、团队日报、本人个人日报、考勤 |

具体用户名/密码见本地 `.env` 的 `AUTH_ADMIN_*` / `AUTH_LEADER_*` / `AUTH_MEMBER_*`；部署前请修改默认密码。

## 本地演示（不连 MySQL）

```bash
cd v1-sdd/backend
python -m scripts.demo
```

使用 SQLite + Mock 数据跑通「采集 → 生成 → 推送」，并在控制台输出团队日报。

## 说明

- 飞书暂用 Mock：`.env` 中 `FEISHU_USE_MOCK=true`，GitHub 仍走真实采集；飞书 21001 修复后改为 `false`，并填 `FEISHU_CHAT_IDS` / `FEISHU_REPORT_CHAT_ID`。
- 考勤当前用 Mock 数据；真实飞书考勤接入后替换采集器。
- 当前为演示环境，未启用登录鉴权；成员 / 组长 / 导师权限为后续项。
- `.env` 已被 git 忽略，只提交 `.env.example`。
- 测试与静态检查：

```bash
cd v1-sdd/backend
pytest -q
ruff check .
```

- 规范文档在 `specs/`，阶段一按 SDD 流程产出；Superpowers 技能仅用于阶段二。
