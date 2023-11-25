from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.core.cbdata import OrderRespondCallback, OrderRespondTimedCallback
from src.services.message import models as message_models
from src.services.message import service as message_service

from . import models


def get_reply_markup_instantly(order_id: int) -> InlineKeyboardMarkup:
    blr = InlineKeyboardBuilder()
    for i in range(1, 5):
        b = OrderRespondTimedCallback(order_id=order_id, time=i * 900).pack()
        blr.add(InlineKeyboardButton(text=f"{i * 15} min", callback_data=b))
    blr.adjust(3)
    return blr.as_markup()


def get_reply_markup_response(order_id: int, *, preorder=False) -> InlineKeyboardMarkup:
    blr = InlineKeyboardBuilder()
    b = OrderRespondCallback(order_id=order_id, preorder=preorder).pack()
    blr.add(InlineKeyboardButton(text="I want this order", callback_data=b))
    return blr.as_markup()


async def pull_create(
    params: models.PullCreate,
) -> models.OrderResponse:
    created, skipped = [], []
    markup = get_reply_markup_response(params.order_id, preorder=params.is_preorder)
    message_type = message_models.MessageType.ORDER if not params.is_preorder else message_models.MessageType.PRE_ORDER
    channel_id = params.channel_id
    msg_in = message_models.MessageCreate(
        order_id=params.order_id, channel_id=channel_id, text=params.text, reply_markup=markup, type=message_type
    )
    msg, msg_status = await message_service.create(msg_in)
    if not msg:
        skipped.append(models.SkippedPull(channel_id=channel_id, status=msg_status))
    else:
        created.append(models.SuccessPull(channel_id=channel_id, message_id=msg.message_id, status=msg_status))
    return models.OrderResponse(created=created, skipped=skipped)


async def pull_update(
    params: models.PullUpdate,
) -> models.OrderResponse:
    updated, skipped = [], []
    msg = await message_service.get_by_channel_id_message_id(params.message.channel_id, params.message.message_id)
    msg_in = message_models.MessageUpdate(
        text=params.text, inline_keyboard=get_reply_markup_response(params.order_id, preorder=params.is_preorder)
    )
    message, msg_status = await message_service.update(msg, msg_in)
    if not message:
        skipped.append(models.SkippedPull(status=msg_status, channel_id=msg.channel_id))
    else:
        updated.append(models.SuccessPull(channel_id=msg.channel_id, message_id=msg.message_id, status=msg_status))
    return models.OrderResponse(updated=updated, skipped=skipped)


async def pull_delete(
    params: models.PullDelete,
) -> models.OrderResponse:
    deleted, skipped = [], []
    msg = await message_service.get_by_channel_id_message_id(params.message.channel_id, params.message.message_id)
    message, msg_status = await message_service.delete(msg)
    if not message:
        skipped.append(models.SkippedPull(status=msg_status, channel_id=msg.channel_id))
    else:
        deleted.append(models.SuccessPull(channel_id=msg.channel_id, message_id=msg.message_id, status=msg_status))
    return models.OrderResponse(deleted=deleted, skipped=skipped)
