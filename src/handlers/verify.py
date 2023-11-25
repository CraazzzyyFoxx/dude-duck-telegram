from aiogram import Router, types
from aiogram.filters import Command, CommandObject

from src.services.auth import service as auth_service
from src.services.render import flows as render_flows

router = Router()


@router.message(Command("verify"), flags={"chat_action": {"is_superuser"}})
async def verify(message: types.Message, command: CommandObject) -> None:
    status = await auth_service.verify(command.args)
    if status:
        await message.answer(render_flows.system("verify_200"))
    else:
        await message.answer(render_flows.system("verify_400"))
