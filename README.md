# 智能日报生成器（课程实践）

本仓库按课程要求，用两种方法各实现一遍同一系统——一个从 GitHub / 飞书 / 邮件等真实工作数据自动生成绩效日报的工具。两套代码相互独立，**v2 不得复用 v1 源代码**。

## 目录结构

```
WorkDailyReport/
├── docs/                 # 课程指导书等文档
├── v1-sdd/               # 阶段一：SDD 规范驱动开发（第 1–2 周）
│   ├── backend/          # FastAPI 后端
│   └── frontend/         # Vue 3 + Vite 前端
└── v2-superpowers/       # 阶段二：Superpowers 工作流（第 3–4 周）
    ├── backend/
    └── frontend/
```

> v1 已实现采集 / 生成 / 推送 / 主编排的完整后端链路，可用 Mock 数据在本地跑通；v2 仍为骨架。真实 GitHub / 飞书 / SMTP / MySQL 需凭证就绪后复测。

## 技术栈

- 后端：Python 3.12、FastAPI、Uvicorn、Pydantic Settings、SQLAlchemy + MySQL（aiomysql）、httpx
- 前端：Vue 3、Vite、Vue Router、Pinia、Axios
- 环境：conda 环境 `work_daily`

## 快速开始

### 后端（两套分别启动）

```bash
conda activate work_daily
cd v1-sdd/backend
pip install -r requirements-dev.txt      # 首次
mysql -h 127.0.0.1 -P 3305 -u root -p < sql/schema.sql   # 首次，建库建表
uvicorn app.main:app --reload --port 8000
```

本地演示（SQLite + Mock，无需外部凭证）：

```bash
python -m scripts.demo
```

- 接口文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/health

### 前端

```bash
cd v1-sdd/frontend
npm install
npm run dev
```

访问 http://localhost:5173 ，Vite 已把 `/api` 代理到 `http://127.0.0.1:8000`。

v2 同理，把 `v1-sdd` 换成 `v2-superpowers`。两套后端默认都用 8000 端口，请勿同时启动（或改端口）。

## 凭证与安全（重要）

GitHub 令牌、飞书 `app_secret`、SMTP 授权码**只写入各 backend 目录下的 `.env`**，该文件已被 `.gitignore` 忽略：

- 不要提交 `.env`，不要把凭证写进代码、README 或截图；
- 需要同步给队友时，只共享 `.env.example`（占位符），真实值各自本地填写；
- `GET /api/health` 只返回凭证「是否就绪」的布尔值，不返回任何密钥内容。

## 规范文档

SDD 要求的三份核心规范（`proposal.md` / `design.md` / `tasks.md`）将在后续阶段放入对应工程的 `specs/` 目录，与代码同库管理。

## 项目级技能

- `.claude/skills/unslop/`：前端优化技能，来自 [heydamir/unslop](https://github.com/heydamir/unslop)，作者 Damir Sokolovsky，许可 CC BY 4.0。仅当前项目使用。
