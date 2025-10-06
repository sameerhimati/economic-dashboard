"""
API routes package.

Exports all route routers.
"""
from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.data import router as data_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.newsletters import router as newsletters_router
from app.api.routes.articles import router as articles_router
from app.api.routes.user_settings import router as user_settings_router
from app.api.routes.bookmarks import router as bookmarks_router
from app.api.routes.admin import router as admin_router

__all__ = [
    "health_router",
    "auth_router",
    "data_router",
    "dashboard_router",
    "newsletters_router",
    "articles_router",
    "user_settings_router",
    "bookmarks_router",
    "admin_router",
]
