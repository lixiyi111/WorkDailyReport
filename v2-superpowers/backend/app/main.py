"""FastAPI 应用入口：仅装配基础中间件与路由，业务功能后续按工作流实现。"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="智能日报生成器 · 基础骨架（业务功能待实现）",
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
