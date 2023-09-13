from aiogram import Router

from . import main

router = Router()
router.include_router(router=main.router)
