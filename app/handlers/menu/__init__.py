from aiogram import Router

from . import main
from . import accounting

router = Router()
router.include_router(router=main.router)
# router.include_router(router=accounting.accounting_dialog)
