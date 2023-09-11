import asyncio

from aiogram import types, Router
from aiogram.filters import Command, CommandObject

from app.services.auth import service as auth_service
from app.services.render import flows as render_flows

router = Router()


@router.message(Command('verify'), flags={'chat_action': {"is_superuser"}})
async def verify(message: types.Message, command: CommandObject):
    status = await auth_service.verify(command.args)
    if status:
        msg = await message.answer(render_flows.system("verify_200"))
    else:
        msg = await message.answer(render_flows.system("verify_400"))
    await asyncio.sleep(5)
    await message.delete()
    await msg.delete()