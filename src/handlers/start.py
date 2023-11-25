from aiogram import Router, types
from aiogram.filters import Command

from src.helpers import process_language
from src.services.render import flows as render_flows

router = Router()


@router.message(Command("start"), flags={"chat_action": {"is_private", "is_auth"}})
async def start(message: types.Message) -> None:
    lang = process_language(message.from_user, None)
    await message.answer(render_flows.base("start", lang))
