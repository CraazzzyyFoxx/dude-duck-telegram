from aiogram import Router, types, Bot
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.cbdata import OrderRespondCallback, OrderRespondYesNoCallback
from app.services.api import flows as api_flows
from app.services.response import flows as response_flows
from app.services.render import flows as render_flows
from app.utils.helpers import try_message
from app.utils.templates import render_template_user

# from . import insta
from . import message

# from . import dialogue


router = Router()


@router.callback_query(OrderRespondCallback.filter())
async def entry_point(call: types.CallbackQuery, callback_data: OrderRespondCallback, bot: Bot, user):
    if await response_flows.get_me_response(call.from_user.id, callback_data.order_id):
        await call.answer(render_template_user("response_403", user), show_alert=True)
        return

    order = await api_flows.get_order(call.from_user.id, callback_data.order_id)
    builder = InlineKeyboardBuilder()
    data = [("Accept", True), ("Decline", False)]
    for row in data:
        builder.add(InlineKeyboardButton(text=row[0],
                                         callback_data=OrderRespondYesNoCallback(
                                             order_id=callback_data.order_id, state=row[1]).pack()))

    configs = await render_flows.get_by_base_name(order)
    data = {"rendered_order": render_flows.render_order(order=order, configs=configs)}
    async with try_message(call=call):
        await bot.send_message(
            call.from_user.id,
            render_template_user("order", user, data=data),
            reply_markup=builder.as_markup()
        )
    await call.answer()


# router.include_router(router=respond.router)
# router.include_router(router=insta.router)
router.include_router(router=message.router)
