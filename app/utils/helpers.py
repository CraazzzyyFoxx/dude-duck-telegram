import contextlib

from aiogram import exceptions
from aiogram.types import CallbackQuery, User
from aiogram.utils.web_app import WebAppUser
from loguru import logger

from app.services.api import schemas as api_schemas

__all__ = ("try_message", "process_language")


@contextlib.asynccontextmanager
async def try_message(call: CallbackQuery = None):
    try:
        yield
    except exceptions.TelegramBadRequest as e:
        logger.error(f"Message didn't send, error={e.__str__()}")
        if call:
            me = await call.bot.get_me()
            await call.answer(url=f"https://t.me/{me.username}?start=Hello")


def process_language(user: User | WebAppUser, user_api: api_schemas.User = None) -> api_schemas.UserLanguage:
    if user_api is None:
        if user.language_code == "ru":
            return api_schemas.UserLanguage.RU
        else:
            return api_schemas.UserLanguage.EN
    else:
        return user_api.language
