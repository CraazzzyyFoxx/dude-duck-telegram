from __future__ import annotations

from typing import cast

from telegram import Update, User, Message
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    ConversationHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    CommandHandler,
    CallbackContext
)
from loguru import logger

from app.schemas import OrderRespond, OrderRespondExtra, OrderID
from app.services.pull import PullService
from app.models import ORDER_CONFIRM_YES_CALLBACK
from app.services.time import TimeService
from app.common import format_err, OrderRender

PRICE, START_DATE, ETA, DONE = range(4)


def get_order_respond(chat_data: dict) -> OrderRespond:
    order = cast(OrderID, chat_data["order"])
    user = cast(User, chat_data["user"])

    extra = OrderRespondExtra(
        price=chat_data["price"],
        start_date=chat_data["start_date"],
        eta=chat_data["eta"]
    )

    data = OrderRespond(
        order_id=order.id,
        user_id=user.id,
        channel_id_booster=chat_data["message"].chat_id,
        message_id_booster=chat_data["message"].id,
        username=user.name,
        extra=extra,
        approved=False,
        strict=True
    )

    return data


async def edit_order(chat_data: dict):
    order = cast(OrderID, chat_data["order"])
    message = cast(Message, chat_data["message"])

    data = get_order_respond(chat_data)

    try:
        await message.edit_text(OrderRender().render(order=order, respond=data).__str__(),
                                parse_mode=ParseMode.HTML)
    except BadRequest:
        pass


async def send_state(chat_data: dict, state: int):
    user: User = chat_data["user"]

    if state == PRICE:
        await user.send_message("Enter your desired <b>price</b> for the order")
    elif state == START_DATE:
        await user.send_message("Enter the <b>start date</b> of the order")
    elif state == ETA:
        await user.send_message("Enter the <b>deadline (eta)</b> for your order")


async def parse_order(update: Update, context: CallbackContext):
    text = update.message.text
    category: int = context.chat_data["choice"]
    user: User = context.chat_data["user"]

    if category == PRICE:
        if text.isdigit():
            context.chat_data["price"] = text
            return True
    elif category != DONE:
        try:
            if category == START_DATE:
                time = TimeService.convert_time(text, future_time=True)
                context.chat_data["start_date"] = time
            else:
                time = TimeService.convert_time(text, future_time=True, now=context.chat_data["start_date"])
                context.chat_data["eta"] = time - context.chat_data["start_date"]

        except ValueError as e:
            await user.send_message(format_err(e.__str__()), parse_mode=ParseMode.HTML)
        else:
            return True


async def respond_order_yes_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return

    try:
        context.chat_data["order"] = context.user_data.pop("order_confirm")
    except KeyError:
        pass
    user = cast(User, update.effective_user)
    context.chat_data["user"] = user
    context.chat_data["choice"] = PRICE
    context.chat_data["message"] = update.effective_message

    await edit_order(context.chat_data)
    await send_state(context.chat_data, PRICE)

    return START_DATE


async def respond_order_no_button_dialogue(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    if not query.data or not query.data.strip():
        return

    await update.effective_message.delete_message()
    context.chat_data.clear()


async def respond_price_order(update: Update, context: CallbackContext):
    if not await parse_order(update, context):
        await send_state(context.chat_data, PRICE)
        return

    context.chat_data["choice"] = START_DATE

    await edit_order(context.chat_data)
    await send_state(context.chat_data, START_DATE)
    return START_DATE


async def respond_start_date_order(update: Update, context: CallbackContext):
    if not await parse_order(update, context):
        await send_state(context.chat_data, PRICE)
        return

    context.chat_data["choice"] = START_DATE

    await edit_order(context.chat_data)
    await send_state(context.chat_data, START_DATE)
    return ETA


async def respond_eta_order_button(update: Update, context: CallbackContext):
    if not await parse_order(update, context):
        await send_state(context.chat_data, START_DATE)
        return

    context.chat_data["choice"] = ETA

    await edit_order(context.chat_data)
    await send_state(context.chat_data, ETA)
    return DONE


async def respond_done_order(update: Update, context: CallbackContext):
    if not await parse_order(update, context):
        await send_state(context.chat_data, ETA)
        return

    user = cast(User, context.chat_data["user"])
    data = get_order_respond(context.chat_data)

    await edit_order(context.chat_data)
    await PullService.pull_respond_strict(data, user)
    await update.effective_user.send_message("Done! Order sent to admins")

    context.chat_data.clear()
    logger.info(f"A user {update.effective_user.username} [ID: {update.effective_user.id}] "
                f"has submitted a request for an order ")
    return ConversationHandler.END


async def stop(update: Update, context: CallbackContext) -> int:
    await update.effective_user.send_message("Submit order canceled!")
    context.chat_data.clear()
    return ConversationHandler.END


order_conversation_dialogue = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(respond_order_yes_button, ORDER_CONFIRM_YES_CALLBACK.regex())
    ],
    states={
        PRICE: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                           respond_price_order),
        ],
        START_DATE: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")),
                           respond_start_date_order),
        ],
        ETA: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), respond_eta_order_button)
        ],
        DONE: [
            MessageHandler(filters.TEXT & ~(filters.COMMAND | filters.Regex("^Done$")), respond_done_order)
        ],

    },
    fallbacks=[CommandHandler("stop", stop)],
    conversation_timeout=300,
)
