"""
API routes package.

Exports all route routers.
"""
from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.data import router as data_router
from app.api.routes.dashboard import router as dashboard_router

__all__ = [
    "health_router",
    "auth_router",
    "data_router",
    "dashboard_router",
]
