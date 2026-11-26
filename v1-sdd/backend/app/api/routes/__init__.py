"""路由聚合：后续各业务模块的路由在此注册。"""

from fastapi import APIRouter

from app.api.routes.attendance import router as attendance_router
from app.api.routes.auth import router as auth_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.health import router as health_router
from app.api.routes.members import router as members_router
from app.api.routes.reports import router as reports_router
from app.api.routes.runs import router as runs_router
from app.api.routes.settings import router as settings_router
from app.api.routes.sources import router as sources_router
from app.api.routes.users import router as users_router
from app.api.routes.work_records import router as work_records_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(dashboard_router)
api_router.include_router(reports_router)
api_router.include_router(work_records_router)
api_router.include_router(members_router)
api_router.include_router(sources_router)
api_router.include_router(runs_router)
api_router.include_router(settings_router)
api_router.include_router(attendance_router)

__all__ = ["api_router"]
