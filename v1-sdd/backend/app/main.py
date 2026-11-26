"""FastAPI 应用入口：装配中间件、路由、建表与定时任务。"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.db.session import init_models
from app.scheduler import start_scheduler, stop_scheduler
from app.services.auth import seed_default_users

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    if settings.auto_create_tables:
        await init_models()
    await seed_default_users()
    if settings.enable_scheduler:
        start_scheduler()
    yield
    if settings.enable_scheduler:
        stop_scheduler()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="智能日报生成器 · v1（SDD）",
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
