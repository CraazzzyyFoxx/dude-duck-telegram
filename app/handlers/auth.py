from aiogram import types, Router
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from app.core import config
from app.helpers import process_language
from app.services.render import flows as render_flows

router = Router()


@router.message(Command('signup'), flags={'chat_action': {"is_private", "is_auth"}})
async def register(message: types.Message):
    lang = process_language(message.from_user, None)
    msg = await message.answer(render_flows.base("register_start_pre", lang))
    web_app = WebAppInfo(url=f"{config.app.auth_url}auth/signup?message_id={msg.message_id}")
    await msg.edit_text(render_flows.base("register_start", lang),
                        reply_markup=InlineKeyboardMarkup(
                            inline_keyboard=[[InlineKeyboardButton(text="Signup", web_app=web_app)]]
                        )
                        )


@router.message(Command("login"), flags={'chat_action': {"is_private", "is_auth"}})
async def command_webview(message: Message):
    lang = process_language(message.from_user, None)
    msg = await message.answer(render_flows.base("login_start_pre", lang))
    web_app = WebAppInfo(url=f"{config.app.auth_url}auth/login?message_id={msg.message_id}")
    await msg.edit_text(render_flows.base("login_start", lang),
                        reply_markup=InlineKeyboardMarkup(
                            inline_keyboard=[[InlineKeyboardButton(text="Login", web_app=web_app)]]
                        )
                        )
