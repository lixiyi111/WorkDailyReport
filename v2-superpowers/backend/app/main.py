"""FastAPI 应用入口：装配中间件、路由、启动初始化与定时任务。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import get_settings
from app.db.session import get_session_factory, init_models
from app.services.auth import seed_default_users

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if settings.auto_create_tables:
        await init_models()
    async with get_session_factory()() as session:
        await seed_default_users(session)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="智能日报生成器 · v2（Superpowers 工作流驱动）",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/", tags=["meta"])
def index() -> dict[str, str]:
    """根路径：返回服务标识与接口文档地址。"""
    return {"service": settings.app_name, "docs": "/docs"}
