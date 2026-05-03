from .auth import router as auth_router
from .projects import router as projects_router
from .tasks import router as tasks_router
from .users import router as users_router

__all__ = [
    "auth_router",
    "projects_router",
    "tasks_router", 
    "users_router"
]