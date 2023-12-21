from aiogram import Router, types, F
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.cbdata import OrderRespondConfirmCallback
from src import models
from src.services.render import flows as render_flows
from src.services.response import flows as response_flows

router = Router()


@router.callback_query(
    OrderRespondConfirmCallback.filter(), flags={"chat_action": {"is_superuser"}}
)  # noqa E712
async def response_update(
        call: types.CallbackQuery,
        callback_data: OrderRespondConfirmCallback,
        session: AsyncSession,
        user: models.UserDB,
) -> None:
    status = await response_flows.update_response(
        session,
        user,
        callback_data.state,
        callback_data.order_id,
        callback_data.user_id,
        preorder=callback_data.preorder,
    )
    if status == 200:
        await call.answer(
            render_flows.system("response_update_200", data={"approved": callback_data.state}), show_alert=True
        )
        return
    if status in (404, 400, 403, 409):
        await call.answer(render_flows.system(f"response_update_{status}"), show_alert=True)
    else:
        await call.answer(render_flows.system("internal_error"), show_alert=True)
