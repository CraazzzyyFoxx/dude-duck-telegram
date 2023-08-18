from fastapi import APIRouter

from app.services.render import views as render_views
from app.services.pull import views as pull_views

from app.services.auth import views as auth_views
from app.services.close import views as close_views
from app.services.message import views as message_views
from app.services.channel import views as channel_views

router = APIRouter()
router.include_router(auth_views.router)
router.include_router(close_views.router)

api_router = APIRouter(prefix="/api")
api_router.include_router(render_views.router)
api_router.include_router(pull_views.router)
api_router.include_router(channel_views.router)

router.include_router(api_router)
