from aiogram import types, Router
from aiogram.filters import Command

from app.helpers import process_language
from app.services.api import flows as auth_flows
from app.services.render import flows as render_flows

router = Router()


@router.message(Command('language'), flags={'chat_action': {"is_private", "is_auth"}})
async def request_verify(message: types.Message) -> None:
    user = await auth_flows.change_language(message.from_user.id)
    await message.answer(render_flows.user("change_language", user))
