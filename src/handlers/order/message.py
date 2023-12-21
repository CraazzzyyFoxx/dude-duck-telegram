from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.bot import bot
from src import models, schemas
from src.core.cbdata import OrderRespondYesNoCallback
from src.services.api import flows as api_flows
from src.services.message import service as message_service
from src.services.render import flows as render_flows
from src.services.response import flows as response_flows

router = Router()


class OrderRespondState(StatesGroup):
    approved = State()


@router.callback_query(OrderRespondYesNoCallback.filter(F.state == True))  # noqa F722
async def respond_order_yes_button(
    call: types.CallbackQuery,
    state: FSMContext,
    callback_data: OrderRespondYesNoCallback,
    user: models.UserDB,
    session: AsyncSession,
) -> None:
    if callback_data.preorder:
        order = await api_flows.get_preorder(user, callback_data.order_id)
    else:
        order = await api_flows.get_order(user, callback_data.order_id)
    msg = await message_service.get_by_channel_id_message_id(session, call.message.chat.id, call.message.message_id)
    await message_service.update(session, msg, models.MessageUpdate())
    await bot.send_message(call.from_user.id, render_flows.user("response_200", user))
    await state.set_state(OrderRespondState.approved)
    await state.update_data(order=order, message=msg, preorder=callback_data.preorder)


@router.callback_query(OrderRespondYesNoCallback.filter(F.state == False))  # noqa F722
async def respond_order_no_button_message(call: types.CallbackQuery) -> None:
    await call.answer()
    if call.message is not None:
        await bot.delete_message(call.message.chat.id, call.message.message_id)


@router.message(OrderRespondState.approved, F.text)
async def respond_done_order(
    message: Message, state: FSMContext, user: models.UserDB, session: AsyncSession
) -> None:
    data = await state.get_data()
    order: schemas.Order = data.get("order")
    msg: models.Message = data.get("message")
    preorder: bool = data.get("preorder")
    extra = schemas.OrderResponseExtra(text=message.text)
    status, resp = await response_flows.create_response(user, order.id, extra, preorder)

    if status in (404, 400, 403, 409):
        await message.answer(render_flows.user(f"response_{status}", user))
        await state.clear()
        return
    await message_service.update(
        session,
        msg,
        models.MessageUpdate(text=await render_flows.get_order_text(user, order.id)),
    )
    await message.answer(render_flows.user("response_201", user))
    await state.clear()
