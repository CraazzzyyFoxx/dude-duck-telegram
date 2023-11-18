from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from app.core.bot import bot
from app.core.cbdata import OrderRespondYesNoCallback
from app.services.api import flows as api_flows
from app.services.api import schemas as api_schemas
from app.services.message import models as message_models
from app.services.message import service as message_service
from app.services.render import flows as render_flows
from app.services.response import flows as response_flows

router = Router()


class OrderRespondState(StatesGroup):
    approved = State()


@router.callback_query(OrderRespondYesNoCallback.filter(F.state == True))  # noqa F722
async def respond_order_yes_button(
    call: types.CallbackQuery, state: FSMContext, callback_data: OrderRespondYesNoCallback, user: api_schemas.User
) -> None:
    if callback_data.preorder:
        order = await api_flows.get_preorder(call.from_user.id, callback_data.order_id)
    else:
        order = await api_flows.get_order(call.from_user.id, callback_data.order_id)
    msg = await message_service.get_by_channel_id_message_id(call.message.chat.id, call.message.message_id)
    await message_service.update(msg, message_models.MessageUpdate())
    await bot.send_message(call.from_user.id, render_flows.user("response_200", user))
    await state.set_state(OrderRespondState.approved)
    await state.update_data(order=order, message=msg, preorder=callback_data.preorder)


@router.callback_query(OrderRespondYesNoCallback.filter(F.state == False))  # noqa F722
async def respond_order_no_button_message(call: types.CallbackQuery) -> None:
    await call.answer()
    await bot.delete_message(call.message.chat.id, call.message.message_id)


@router.message(OrderRespondState.approved, F.text)
async def respond_done_order(message: Message, state: FSMContext, user: api_schemas.User) -> None:
    data = await state.get_data()
    order = data.get("order")
    msg: message_models.Message = data.get("message")
    preorder: bool = data.get("preorder")
    extra = response_flows.models.OrderResponseExtra(text=message.text)
    status, resp = await response_flows.create_response(message.from_user.id, order.id, extra, preorder)

    if status in (404, 400, 403, 409):
        await message.answer(render_flows.user(f"response_{status}", user))
        await state.clear()
        return
    data = {"order": order, "response": resp, "user": await api_flows.get_me_user_id(message.from_user.id)}
    configs = render_flows.get_order_configs(order, is_pre=preorder)
    await message_service.update(msg, message_models.MessageUpdate(text=await render_flows.order(configs, data=data)))
    await message.answer(render_flows.user("response_201", user))
    await state.clear()
