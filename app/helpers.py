from aiogram.types import User
from aiogram.utils.web_app import WebAppUser

from app.services.api import schemas as api_schemas

__all__ = ("process_language",)


def process_language(user: User | WebAppUser, user_api: api_schemas.User = None) -> api_schemas.UserLanguage:
    if user_api is None:
        if user.language_code == "ru":
            return api_schemas.UserLanguage.RU
        else:
            return api_schemas.UserLanguage.EN
    else:
        return user_api.language
