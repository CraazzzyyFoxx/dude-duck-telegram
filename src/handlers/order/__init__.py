from aiogram import Router, types
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cbdata import OrderRespondCallback, OrderRespondYesNoCallback
from src.services.api import flows as api_flows
from src import models
from src.services.message import service as message_service
from src.services.render import flows as render_flows
from src.services.response import service as response_service

from . import insta, message

router = Router()


@router.callback_query(OrderRespondCallback.filter())
async def entry_point(
    call: types.CallbackQuery,
    callback_data: OrderRespondCallback,
    user: models.UserDB,
    session: AsyncSession,
) -> None:
    if await response_service.get_me_response(user, callback_data.order_id):
        await call.answer(render_flows.user("response_403", user), show_alert=True)
        return
    if not callback_data.preorder:
        order = await api_flows.get_order(user, callback_data.order_id)
    else:
        order = await api_flows.get_preorder(user, callback_data.order_id)
    builder = InlineKeyboardBuilder()
    data = [("Accept", True), ("Decline", False)]
    for row in data:
        call_data = OrderRespondYesNoCallback(
            order_id=callback_data.order_id,
            state=row[1],
            preorder=callback_data.preorder,
        )
        builder.add(InlineKeyboardButton(text=row[0], callback_data=call_data.pack()))
    msg, status = await message_service.create(
        session,
        models.MessageCreate(
            channel_id=call.from_user.id,
            text=await render_flows.get_order_text(user, order.id),
            type=models.MessageType.MESSAGE,
            reply_markup=builder.as_markup(),
        ),
    )
    if status == models.CallbackStatus.FORBIDDEN:
        me = await call.bot.get_me()
        await call.answer(url=f"https://t.me/{me.username}?start=Hello")
    await call.answer()


router.include_router(router=insta.router)
router.include_router(router=message.router)
