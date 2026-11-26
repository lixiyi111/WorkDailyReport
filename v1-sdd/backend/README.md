# 智能日报生成器 · v1（SDD）后端

FastAPI 基础骨架，仅包含配置加载、CORS、健康检查与冒烟测试。业务功能按 `specs/` 规范后续实现。

## 目录

```
backend/
├── app/
│   ├── main.py            # 应用入口：中间件 + 路由装配
│   ├── core/config.py     # 配置（环境变量 / .env）
│   ├── api/routes/        # 接口路由
│   ├── models/            # ORM 模型（待实现）
│   ├── schemas/           # Pydantic 模型（待实现）
│   └── services/          # 业务服务（采集/生成/推送，待实现）
├── tests/                 # 冒烟测试
├── requirements.txt
├── requirements-dev.txt
└── .env.example
```

## 运行

```bash
conda activate work_daily
pip install -r requirements.txt        # 首次
uvicorn app.main:app --reload --port 8000
```

## 配置

```bash
cp .env.example .env    # 然后填入真实凭证
```

`.env` 已被 git 忽略。健康检查 `GET /api/health` 只显示三类凭证是否就绪，不返回凭证值。

## 数据库（MySQL）

本项目使用 MySQL（`aiomysql` + SQLAlchemy）。首次运行前：

1. 在 `.env` 填写 `DB_HOST` / `DB_PORT` / `DB_USER` / `DB_PASSWORD` / `DB_NAME`；
2. 在 MySQL 中创建数据库（字符集 utf8mb4）：

```sql
CREATE DATABASE daily_report DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

数据库表结构将在功能阶段按规范实现。

## 验证

```bash
pytest            # 冒烟测试
ruff check .      # 静态扫描（阶段规范要求）
```
