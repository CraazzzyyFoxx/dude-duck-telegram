import datetime

from aiogram import Router, types

from app.core.bot import bot
from app.core.cbdata import OrderRespondCallback
from app.services.api import flows as api_flows
from app.services.api import schemas as api_schemas
from app.services.render import flows as render_flows
from app.services.response import flows as response_flows

router = Router()


@router.callback_query(OrderRespondCallback.filter(), flags={"is_verified"})
async def respond_order_button(
    call: types.CallbackQuery, callback_data: OrderRespondCallback, user: api_schemas.User
) -> None:
    order = await api_flows.get_order(call.from_user.id, callback_data.order_id)
    extra = response_flows.models.OrderResponseExtra(eta=datetime.timedelta(seconds=callback_data.time))
    resp = await response_flows.create_response(call.from_user.id, order.id, extra)
    await bot.send_message(call.from_user.id, render_flows.user(f"response_{resp}", user))
    await call.answer()
