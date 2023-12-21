from aiogram import Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cbdata import VerifyCallback
from src import models
from src.services.auth import service as auth_service
from src.services.render import flows as render_flows
from src.services.message import service as message_service

router = Router()


@router.callback_query(VerifyCallback.filter(F.state == True), flags={"chat_action": {"is_superuser"}})  # noqa F722
async def verify_yes(
    call: types.CallbackQuery,
    callback_data: VerifyCallback,
    user: models.UserDB,
    session: AsyncSession,
) -> None:
    status = await auth_service.verify(user, callback_data.user_id)
    if status:
        await call.answer(render_flows.system("verify_200"), show_alert=True)
    else:
        await call.answer(render_flows.system("verify_400"), show_alert=True)
    message = await message_service.get_by_channel_id_message_id(session, call.message.chat.id, call.message.message_id)
    await message_service.delete(session, message)


@router.callback_query(VerifyCallback.filter(F.state == False), flags={"chat_action": {"is_superuser"}})  # noqa F722
async def verify_yes(
    call: types.CallbackQuery,
    session: AsyncSession,
) -> None:
    message = await message_service.get_by_channel_id_message_id(session, call.message.chat.id, call.message.message_id)
    await message_service.delete(session, message)
