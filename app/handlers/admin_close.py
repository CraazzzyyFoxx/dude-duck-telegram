from aiogram import Router, types

from app.core.cbdata import OrderRespondConfirmCallback
from app.services.response import flows as response_flows

router = Router()


@router.callback_query(OrderRespondConfirmCallback.filter(), flags={'chat_action': {"is_superuser"}})
async def close_order(call: types.CallbackQuery, callback_data: OrderRespondConfirmCallback):
    await response_flows.approve_response(call.from_user.id, callback_data.order_id, callback_data.user_id)
    await call.answer()
