import datetime

from aiogram import Router, types

from app.core.bot import bot
from app.core.cbdata import OrderRespondCallback
from app.services.api import flows as api_flows
from app.services.response import flows as response_flows
from app.utils.templates import render_template_user


router = Router()


@router.callback_query(OrderRespondCallback.filter(), flags={"is_verified"})
async def respond_order_button(call: types.CallbackQuery, callback_data: OrderRespondCallback, user):
    order = await api_flows.get_order(call.from_user.id, callback_data.order_id)
    extra = response_flows.models.OrderResponseExtra(eta=datetime.timedelta(seconds=callback_data.time))
    resp = await response_flows.create_response(call.from_user.id, order.id, extra)
    if resp == 404:
        await bot.send_message(call.from_user.id, render_template_user("response_404", user))
        return
    if resp == 400:
        await bot.send_message(call.from_user.id, render_template_user("response_400", user))
        return
    if resp == 403:
        await bot.send_message(call.from_user.id, render_template_user("response_403", user))
        return

    await bot.send_message(call.from_user.id, render_template_user("response_201", user))
    await call.answer()
