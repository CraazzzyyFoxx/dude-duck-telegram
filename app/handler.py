from aiogram import Router

from app.handlers import auth
from app.handlers import start
from app.handlers import menu
from app.handlers import admin_close
from app.handlers import order
from app.handlers import request_verify
from app.handlers import verify
from app.handlers import get_id
from app.handlers import language


dialog_router = Router()


router = Router()
router.include_router(router=start.router)
router.include_router(router=admin_close.router)
router.include_router(router=order.router)
router.include_router(router=request_verify.router)
router.include_router(router=verify.router)
router.include_router(router=auth.router)
router.include_router(router=dialog_router)
router.include_router(router=menu.router)
router.include_router(router=get_id.router)
router.include_router(router=language.router)
