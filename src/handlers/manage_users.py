from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from src.core import config
from src.services.render import flows as render_flows

router = Router()


@router.message(Command("manage_users"), flags={"chat_action": {"is_private", "is_superuser"}})
async def update_user(message: types.Message) -> None:
    web_app = WebAppInfo(url=f"{config.app.auth_url}bot/users?user_id={message.from_user.id}")
    await message.answer(
        render_flows.system("update_user"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Users", web_app=web_app)]]),
    )
