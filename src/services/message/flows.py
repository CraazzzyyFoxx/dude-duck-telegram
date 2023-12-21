from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from src import models
from src.core.cbdata import OrderRespondCallback, OrderRespondTimedCallback
from src.services.message import service as message_service



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


async def create_order_message(
    session: AsyncSession,
    params: models.OrderMessageCreate,
) -> models.MessageCallback:
    created, skipped = [], []
    markup = get_reply_markup_response(params.order_id, preorder=params.is_preorder)
    message_type = models.MessageType.ORDER if not params.is_preorder else message_models.MessageType.PRE_ORDER
    channel_id = params.channel_id
    msg_in = models.MessageCreate(
        order_id=params.order_id,
        channel_id=channel_id,
        text=params.text,
        reply_markup=markup,
        type=message_type,
    )
    msg, msg_status = await message_service.create(session, msg_in)
    if not msg:
        skipped.append(models.SkippedCallback(channel_id=channel_id, status=msg_status))
    else:
        created.append(models.SuccessCallback(channel_id=channel_id, message_id=msg.message_id, status=msg_status))
    return models.MessageCallback(created=created, skipped=skipped)


async def update_order_message(
    session: AsyncSession,
    params: models.OrderMessageUpdate,
) -> models.MessageCallback:
    updated, skipped = [], []
    msg = await message_service.get_by_channel_id_message_id(
        session, params.message.channel_id, params.message.message_id
    )
    msg_in = models.MessageUpdate(
        text=params.text,
        inline_keyboard=get_reply_markup_response(params.message.order_id, preorder=params.message.is_preorder),
    )
    message, msg_status = await message_service.update(session, msg, msg_in)
    if not message:
        skipped.append(models.SkippedCallback(status=msg_status, channel_id=msg.channel_id))
    else:
        updated.append(models.SuccessCallback(channel_id=msg.channel_id, message_id=msg.message_id, status=msg_status))
    return models.MessageCallback(updated=updated, skipped=skipped)


async def delete_order_message(
    session: AsyncSession,
    params: models.OrderMessageDelete,
) -> models.MessageCallback:
    deleted, skipped = [], []
    msg = await message_service.get_by_channel_id_message_id(
        session, params.message.channel_id, params.message.message_id
    )
    message, msg_status = await message_service.delete(session, msg)
    if not message:
        skipped.append(models.SkippedCallback(status=msg_status, channel_id=msg.channel_id))
    else:
        deleted.append(models.SuccessCallback(channel_id=msg.channel_id, message_id=msg.message_id, status=msg_status))
    return models.MessageCallback(deleted=deleted, skipped=skipped)
