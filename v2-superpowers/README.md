# 智能日报生成器 · v2（Superpowers）

用 Superpowers 工作流从零重写的智能日报系统：采集 GitHub 提交、飞书任务与群消息，生成个人/团队日报，支持邮件、飞书机器人与控制台推送。

> 阶段一（v1-SDD）在 `../v1-sdd/`；本目录是阶段二，**业务代码从零实现，不复制 v1 源码**。只继承文字形式的设计结论（见 `docs/03-v2设计输入.md`）。

## 技术栈

- 后端：Python 3.12、FastAPI、SQLAlchemy 2.x（async）、aiomysql、httpx、APScheduler、PyJWT
- 前端：Vue 3、Vite、Vue Router、Pinia、Axios、marked、DOMPurify、lucide
- 数据库：MySQL 8（`127.0.0.1:3305`，库 `daily_report_v2`）

## 目录

```
v2-superpowers/
├── backend/
│   ├── app/
│   │   ├── core/            # 配置、时间窗口、契约、重试、日志脱敏
│   │   ├── db/              # Base、异步会话
│   │   ├── models/          # 13 张 ORM 表
│   │   ├── schemas/         # 请求模型
│   │   ├── services/        # 采集 / 生成 / 推送 / 编排 / 认证
│   │   ├── api/routes/      # REST API
│   │   └── scheduler.py     # 次日 09:00 定时任务
│   ├── sql/                 # schema.sql / demo_members.sql
│   ├── tests/               # TDD 测试（65+）
│   └── requirements*.txt
├── frontend/                # Vue 3 + Vite
└── docs/                    # 方法回顾、初始化记录、设计输入、tasks、验收
```

## 运行

### 1. 环境

- `conda activate work_daily`（Python 3.12；**不要用 base 的 3.9**）
- MySQL 8 运行在 `127.0.0.1:3305`
- Node.js 20+

### 2. 数据库

```bash
cd v2-superpowers/backend
mysql -h 127.0.0.1 -P 3305 -u root -p < sql/schema.sql
mysql -h 127.0.0.1 -P 3305 -u root -p -D daily_report_v2 < sql/demo_members.sql
```

`demo_members.sql` 创建 3 个演示成员（王芳 / 李四 / 赵敏）与飞书 Mock 身份。

> `schema.sql` 使用 `CREATE TABLE IF NOT EXISTS`，**可以重复执行**；已存在的表会被跳过，不会改动其结构。
> 如需彻底重建（会删除 v2 的全部数据）：
>
> ```bash
> mysql -h 127.0.0.1 -P 3305 -u root -p -e "DROP DATABASE IF EXISTS daily_report_v2"
> mysql -h 127.0.0.1 -P 3305 -u root -p < sql/schema.sql
> mysql -h 127.0.0.1 -P 3305 -u root -p -D daily_report_v2 < sql/demo_members.sql
> ```

### 3. 后端

```bash
cd v2-superpowers/backend
pip install -r requirements-dev.txt
cp .env.example .env      # 填入凭证；数据库默认 3305 / daily_report_v2
uvicorn app.main:app --reload --port 8000
```

- API 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/health

### 4. 前端

```bash
cd v2-superpowers/frontend
npm install
npm run dev
```

访问 http://localhost:5173/login。

## 演示账号

首次启动按 `.env` 自动创建（部署前请修改）：

| 用户名 | 密码 | 角色 | 可见范围 |
|--------|------|------|----------|
| `admin` | `admin123` | 管理员 | 全部 |
| `leader` | `leader123` | 组长 | 除账号管理外的管理功能 |
| `member` | `member123` | 成员 | 团队日报 + 本人个人日报 |

成员账号通过 `AUTH_MEMBER_ID` 绑定到 `members.id`（演示默认 1 = 王芳）。

## 功能

- 采集：GitHub 提交（真实，需 `GITHUB_TOKEN`）、飞书任务/消息（`FEISHU_USE_MOCK=true` 走 Mock）、Mock 采集兜底
- 生成：身份解析、协作归属、个人日报四段式、团队日报四段式、Markdown 渲染
- 推送：SMTP 邮件、飞书机器人、控制台；逐次写 `push_logs`
- 存储：原始数据与日报 MySQL 持久化；自然键幂等，重跑不重复
- 接口：登录/当前用户、日报查询/详情/编辑/生成/推送、成员、身份绑定、未归属、数据源状态、推送记录
- 前端：登录、工作台、日报列表/详情/编辑/导出、数据源状态、身份绑定、推送记录

## 测试与静态检查

```bash
cd v2-superpowers/backend
pytest -q
ruff check .
```

前端构建：

```bash
cd v2-superpowers/frontend
npm run build
```

## 文档

| 文件 | 内容 |
|------|------|
| `docs/01-方法切换回顾.md` | SDD 与 Superpowers 的对比、切换决定 |
| `docs/02-v2初始化记录.md` | 仓库/目录/数据库/工作流/提交纪律 |
| `docs/03-v2设计输入.md` | 从 v1 继承的需求、ADR、表结构经验、接口契约 |
| `docs/04-v2-tasks.md` | 任务清单、依赖图、TDD 模板、评审节点 |
| `docs/05-提交规范说明.md` | 两阶段提交格式与不改写历史的原因 |
| `docs/验收核对表.md` | F/P/B 验收结果与证据 |
| `docs/功能对齐表.md` | v1 与 v2 功能对照及差异决定 |

## 说明

- 飞书 `21001` 未解决前保持 `FEISHU_USE_MOCK=true`；GitHub 已同步 v1 的 token，2026-11-26 实测采集 23 条，未配置 token 时自动回退 Mock。
- 凭证只放 `backend/.env`，该文件已被 git 忽略；仓库内只有 `.env.example`。可用 `python -m scripts.sync_env_from_v1 ../../v1-sdd/backend/.env .env` 从 v1 同步凭证（不打印值）。
- 账号密码与 `AUTH_SECRET` 仅用于本地演示，部署前必须更换。
