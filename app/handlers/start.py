from aiogram import types, Router
from aiogram.filters import Command

from app.utils.helpers import process_language
from app.utils.templates import render_template

router = Router()


@router.message(Command('start'), flags={'chat_action': {"is_private", "is_auth"}})
async def start(message: types.Message):
    lang = process_language(message.from_user, None)
    await message.answer(render_template("start", lang))
