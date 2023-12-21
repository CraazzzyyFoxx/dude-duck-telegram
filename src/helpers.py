from aiogram.types import User
from aiogram.utils.web_app import WebAppUser

from src import models, schemas


__all__ = ("process_language",)


def process_language(
    user: User | WebAppUser | None, user_api: models.UserDB | None = None
) -> schemas.UserLanguage:
    if user_api is None:
        if user is not None:
            if user.language_code == "ru":
                return schemas.UserLanguage.RU
            else:
                return schemas.UserLanguage.EN
        else:
            return schemas.UserLanguage.EN
    else:
        return user_api.language
