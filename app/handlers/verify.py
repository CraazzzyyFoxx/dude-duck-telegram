import asyncio

from aiogram import types, Router
from aiogram.filters import Command, CommandObject

from app.services.auth import service as auth_service

router = Router()


@router.message(Command('verify'), flags={'chat_action': {"is_superuser"}})
async def verify(message: types.Message, command: CommandObject):
    await auth_service.verify(command.args)
    msg = await message.answer("Success")
    await asyncio.sleep(5)
    await message.delete()
    await msg.delete()
