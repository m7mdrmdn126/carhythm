from .admin import router as admin_router
from .admin_panel import router as admin_panel_router
from .examination import router as examination_router

__all__ = ["admin_router", "admin_panel_router", "examination_router"]