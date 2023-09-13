from aiogram import Router, types
from aiogram.filters import Command

from app.helpers import process_language
from app.services.auth import service as auth_service
from app.services.render import flows as render_flows

router = Router()


@router.message(Command('request_verify'), flags={'chat_action': {"is_private", "is_auth"}})
async def request_verify(message: types.Message, user) -> None:
    lang = process_language(message.from_user, None)
    if user is None:
        await message.answer(render_flows.base("verify_request_404", lang))
        return
    await auth_service.request_verify(message.from_user.id)
    await message.answer(render_flows.user("verify_request", user))
