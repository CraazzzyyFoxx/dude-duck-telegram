from enum import StrEnum

from aiogram.types import BotCommand

__all__ = ("RouteTag",)


class RouteTag(StrEnum):
    """Tags used to classify API routes"""

    ORDER_CHANNELS = "🧷 Telegram Channels"
    ORDER_MESSAGES = "✉️ Telegram Order Messages"
    ORDER_RENDERS = " 🔪 Order Render Templates"
    NOTIFICATIONS = "🔔 Notifications"
    AUTH = "🤷🏿‍♀️‍ Auth"
    USERS = "🤷🏿‍♀️‍ Users"
    CLOSE = "Close Order"


class Integration(StrEnum):
    discord = "discord"
    telegram = "telegram"


my_commands_en = [
    BotCommand(command="start", description="Start a dialogue with the bot"),
    BotCommand(command="signup", description="Start the registration process"),
    BotCommand(command="login", description="Start the authorization process"),
    BotCommand(command="request_verify", description="Starts the verification process"),
    BotCommand(command="menu", description="Opens a menu with detailed information about you"),
]


my_commands_ru = [
    BotCommand(command="start", description="Начинает диалог с ботом"),
    BotCommand(command="signup", description="Начинает процесс регистрации"),
    BotCommand(command="login", description="Начинает процесс авторизации"),
    BotCommand(command="request_verify", description="Начинает процесс верификации"),
    BotCommand(command="menu", description="Открывает меню с подробной информацией о вас"),
]
