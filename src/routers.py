from fastapi import APIRouter

from src.services.auth import views as auth_views
from src.services.close import views as close_views
from src.services.message import views as message_views
from src.services.notifications import views as notifications_views
from src.services.users import views as users_views

router = APIRouter()
router.include_router(auth_views.router)
router.include_router(close_views.router)
router.include_router(users_views.router)

api_router = APIRouter(prefix="/api")
api_router.include_router(message_views.router)
api_router.include_router(notifications_views.router)

router.include_router(api_router)
