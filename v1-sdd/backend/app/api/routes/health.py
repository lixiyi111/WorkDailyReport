"""健康检查：只报告凭证「是否就绪」，绝不返回凭证值。"""

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "status": "ok",
        "app_env": settings.app_env,
        "feishu_mode": "mock" if settings.feishu_use_mock else "live",
        "credentials": {
            "github": bool(settings.github_token),
            "feishu": bool(settings.feishu_app_id and settings.feishu_app_secret),
            "smtp": bool(settings.smtp_user and settings.smtp_auth_code),
        },
    }
