from aiogram import types, Router
from aiogram.filters import Command
from loguru import logger

from app.utils.helpers import process_language
from app.utils.templates import render_template
from app.services.auth import service as auth_service

router = Router()


@router.message(Command('request_verify'), flags={'chat_action': {"is_private", "is_auth"}})
async def request_verify(message: types.Message) -> None:
    await auth_service.request_verify(message.from_user.id)
    lang = process_language(message.user, None)
    await message.answer(render_template("verify_request", lang))
