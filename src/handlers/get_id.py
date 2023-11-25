from aiogram import Router, types
from aiogram.filters import Command

from src.services.render import flows as render_flows

router = Router()


@router.message(Command("get_id"), flags={"chat_action": {"is_superuser"}})
async def get_id(message: types.Message) -> None:
    await message.answer(
        render_flows.system("get_id", data={"channel_id": message.chat.id, "channel_type": message.chat.type})
    )
