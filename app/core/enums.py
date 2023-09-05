from enum import StrEnum

from aiogram.types import BotCommand

__all__ = ("RouteTag",)


class RouteTag(StrEnum):
    """Tags used to classify API routes"""

    ORDER_CHANNELS = "🧷 Telegram Channels"
    ORDER_MESSAGES = "✉️ Telegram Order Messages"
    ORDER_RENDERS = " 🔪 Order Render Templates"
    AUTH = "🤷🏿‍♀️‍ Auth"
    CLOSE = "Close Order"


my_commands_en = [
    BotCommand(command="start", description="Start a dialogue with the bot"),
    BotCommand(command="signup", description="Start the registration process"),
    BotCommand(command="login", description="Start the authorization process"),
    BotCommand(command="request_verify", description="Starts the verification process"),
    BotCommand(command="menu", description="Opens a menu with detailed information about you"),
    BotCommand(command="language", description="Changes the current language, if RU then to EN and vice versa")
]


my_commands_ru = [
    BotCommand(command="start", description="Начинает диалог с ботом"),
    BotCommand(command="signup", description="Начинает процесс регистрации"),
    BotCommand(command="login", description="Начинает процесс авторизации"),
    BotCommand(command="request_verify", description="Начинает процесс верификации"),
    BotCommand(command="menu", description="Открывает меню с подробной информацией о вас"),
    BotCommand(command="language", description="Меняет текущий язык, если RU, то на EN и наоборот")
]
