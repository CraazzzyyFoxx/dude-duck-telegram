import datetime

from aiogram import Router, types

from src.core.bot import bot
from src import models, schemas
from src.core.cbdata import OrderRespondCallback
from src.services.api import flows as api_flows
from src.services.render import flows as render_flows
from src.services.response import flows as response_flows

router = Router()


@router.callback_query(OrderRespondCallback.filter(), flags={"is_verified"})
async def respond_order_button(
    call: types.CallbackQuery,
    callback_data: OrderRespondCallback,
    user: models.UserDB,
) -> None:
    order = await api_flows.get_order(user, callback_data.order_id)
    extra = schemas.OrderResponseExtra(eta=datetime.timedelta(seconds=callback_data.time))
    resp = await response_flows.create_response(user, order.id, extra)
    await bot.send_message(call.from_user.id, render_flows.user(f"response_{resp}", user))
    await call.answer()
