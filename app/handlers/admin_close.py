from aiogram import Router, types

from app.core.cbdata import OrderRespondConfirmCallback
from app.services.render import flows as render_flows
from app.services.response import flows as response_flows

router = Router()


@router.callback_query(OrderRespondConfirmCallback.filter(), flags={'chat_action': {"is_superuser"}})
async def close_order(call: types.CallbackQuery, callback_data: OrderRespondConfirmCallback):
    if callback_data.preorder:
        status = await response_flows.approve_response(
            call.from_user.id, callback_data.order_id, callback_data.user_id, preorder=True
        )
    else:
        status = await response_flows.approve_response(
            call.from_user.id, callback_data.order_id, callback_data.user_id, preorder=False
        )
    if status is None:
        await call.answer()
    elif status in (404, 400, 403, 409):
        await call.answer(render_flows.system(f"response_approve_{status}"), show_alert=True)
    else:
        await call.answer(render_flows.system("internal_error"), show_alert=True)
