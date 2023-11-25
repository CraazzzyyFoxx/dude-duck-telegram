from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from src.core import config
from src.helpers import process_language
from src.services.render import flows as render_flows

router = Router()


@router.message(Command("signup"), flags={"chat_action": {"is_private", "is_auth"}})
async def register(message: types.Message) -> None:
    lang = process_language(message.from_user, None)
    msg = await message.answer(render_flows.base("register_start_pre", lang))
    web_app = WebAppInfo(url=f"{config.app.auth_url}bot/auth/signup?message_id={msg.message_id}")
    await msg.edit_text(
        render_flows.base("register_start", lang),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Signup", web_app=web_app)]]),
    )


@router.message(Command("login"), flags={"chat_action": {"is_private", "is_auth"}})
async def command_webview(message: Message) -> None:
    lang = process_language(message.from_user, None)
    msg = await message.answer(render_flows.base("login_start_pre", lang))
    web_app = WebAppInfo(url=f"{config.app.auth_url}bot/auth/login?message_id={msg.message_id}")
    await msg.edit_text(
        render_flows.base("login_start", lang),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Login", web_app=web_app)]]),
    )
