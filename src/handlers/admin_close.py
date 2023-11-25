from aiogram import Router, types

from src.core.cbdata import OrderRespondConfirmCallback
from src.services.render import flows as render_flows
from src.services.response import flows as response_flows

router = Router()


@router.callback_query(OrderRespondConfirmCallback.filter(), flags={"chat_action": {"is_superuser"}})
async def close_order(call: types.CallbackQuery, callback_data: OrderRespondConfirmCallback) -> None:
    status = await response_flows.approve_response(
        call.from_user.id, callback_data.order_id, callback_data.user_id, preorder=callback_data.preorder
    )
    if status in (200, 404, 400, 403, 409):
        await call.answer(render_flows.system(f"response_approve_{status}"), show_alert=True)
    else:
        await call.answer(render_flows.system("internal_error"), show_alert=True)
