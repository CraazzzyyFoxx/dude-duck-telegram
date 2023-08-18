from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

from app.core.bot import bot
from app.core.cbdata import OrderRespondYesNoCallback
from app.services.api import flows as api_flows
from app.services.response import flows as response_flows
from app.services.render import flows as render_flows
from app.utils.templates import render_template_user

router = Router()


class OrderRespondState(StatesGroup):
    approved = State()


@router.callback_query(OrderRespondYesNoCallback.filter(F.state == True))
async def respond_order_yes_button(
        call: types.CallbackQuery,
        state: FSMContext,
        callback_data: OrderRespondYesNoCallback,
        user
):
    order = await api_flows.get_order(call.from_user.id, callback_data.order_id)
    configs = await render_flows.get_by_base_name(order)
    text = render_flows.render_order(order=order, configs=configs)
    await bot.edit_message_text(render_template_user("order", user, data={"rendered_order": text}),
                                call.from_user.id, call.message.message_id, reply_markup=None)
    await bot.send_message(call.from_user.id, render_template_user("response_200", user))
    await state.set_state(OrderRespondState.approved)
    await state.update_data(order=order, message=call.message)


@router.callback_query(OrderRespondYesNoCallback.filter(F.state == False))
async def respond_order_no_button_message(call: types.CallbackQuery):
    await call.answer()
    await bot.delete_message(call.message.chat.id, call.message.message_id)


@router.message(OrderRespondState.approved, F.text)
async def respond_done_order(message: Message, state: FSMContext, user):
    data = await state.get_data()
    order = data.get("order")
    msg: Message = data.get("message")
    extra = response_flows.models.OrderResponseExtra(text=message.text)
    resp = await response_flows.create_response(message.from_user.id, order.id, extra)

    if resp == 404:
        await message.answer(render_template_user("response_404", user.user))
        return
    if resp == 400:
        await message.answer(render_template_user("response_400", user.user))
        return
    if resp == 403:
        await message.answer(render_template_user("response_403", user.user))
        return

    configs = await render_flows.get_by_base_name(order)
    text = render_flows.render_order(order=order, configs=configs)
    text = render_template_user("order", user.user, data={"rendered_order": text})
    try:
        await bot.edit_message_text(
            text,
            message.from_user.id,
            msg.message_id
        )
    except TelegramBadRequest:
        pass

    await message.answer(render_template_user("response_201", user.user))
    await state.clear()
