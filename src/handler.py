from aiogram import Router

from src.handlers import (
    admin_close,
    auth,
    get_id,
    manage_users,
    menu,
    order,
    order_message,
    request_verify,
    start,
    verify,
)

router = Router()
router.include_router(router=start.router)
router.include_router(router=admin_close.router)
router.include_router(router=order.router)
router.include_router(router=request_verify.router)
router.include_router(router=verify.router)
router.include_router(router=auth.router)
router.include_router(router=menu.router)
router.include_router(router=get_id.router)
router.include_router(router=manage_users.router)
router.include_router(router=order_message.router)
