from aiogram.exceptions import (TelegramBadRequest, TelegramForbiddenError,
                                TelegramNotFound)

from app.core.bot import bot

from . import models


async def get(message_id: int) -> models.Message | None:
    return await models.Message.filter(id=message_id).first()


async def get_by_type(message_id: int, message_type: models.MessageType) -> list[models.Message]:
    return await models.Message.filter(id=message_id, type=message_type).all()


async def get_by_order_id(order_id: int, preorder: bool) -> list[models.Message]:
    message_type = models.MessageType.PRE_ORDER if preorder else models.MessageType.ORDER
    return await models.Message.filter(order_id=order_id, type=message_type).all()


async def get_by_user_id(user_id: int) -> list[models.Message]:
    return await models.Message.filter(user_id=user_id).all()


async def get_by_order_id_user_id(order_id: int, user_id: int) -> models.Message | None:
    return await models.Message.filter(user_id=user_id, order_id=order_id).first()


async def get_by_order_id_type(order_id: int, message_type: models.MessageType) -> list[models.Message]:
    return await models.Message.filter(order_id=order_id, type=message_type).all()


async def get_by_order_id_channel_id(order_id: int, channel_id: int) -> list[models.Message]:
    return await models.Message.filter(order_id=order_id, channel_id=channel_id).all()


async def get_by_channel_id_message_id(channel_id: int, message_id: int) -> models.Message:
    return await models.Message.filter(channel_id=channel_id, message_id=message_id).first()


async def _create(message_in: models.MessageCreate):
    try:
        msg = await bot.send_message(message_in.channel_id, message_in.text, reply_markup=message_in.reply_markup)
    except TelegramForbiddenError:
        return None, models.MessageStatus.FORBIDDEN

    message_db = await models.Message.create(
        message_id=msg.message_id, **message_in.model_dump(exclude_unset=True, exclude_none=True)
    )
    return message_db, models.MessageStatus.CREATED


async def create_order(message_in: models.MessageCreate) -> tuple[models.Message | None, models.MessageStatus]:
    messages = await get_by_order_id_type(message_in.order_id, message_in.type)
    channels_id = [msg.channel_id for msg in messages]
    if message_in.channel_id not in channels_id:
        return await _create(message_in)
    return None, models.MessageStatus.EXISTS


async def create_response(message_in: models.MessageCreate) -> tuple[models.Message | None, models.MessageStatus]:
    message = await get_by_order_id_user_id(message_in.order_id, message_in.user_id)
    if message is None:
        return await _create(message_in)
    return None, models.MessageStatus.EXISTS


async def create(message_in: models.MessageCreate) -> tuple[models.Message | None, models.MessageStatus]:
    if message_in.type == models.MessageType.ORDER:
        return await create_order(message_in)
    elif message_in.type == models.MessageType.PRE_ORDER:
        return await create_order(message_in)
    elif message_in.type == models.MessageType.RESPONSE:
        return await create_response(message_in)

    return await _create(message_in)


async def update(
    message: models.Message, message_in: models.MessageUpdate
) -> tuple[models.Message | None, models.MessageStatus]:
    try:
        if message_in.text is None and message_in.inline_keyboard is None:
            await bot.edit_message_reply_markup(
                message.channel_id, message.message_id, reply_markup=message_in.inline_keyboard
            )
        else:
            await bot.edit_message_text(
                message_in.text, message.channel_id, message.message_id, reply_markup=message_in.inline_keyboard
            )
    except TelegramBadRequest:
        return None, models.MessageStatus.SAME_TEXT
    except TelegramNotFound:
        await message.delete()
        return None, models.MessageStatus.NOT_FOUND
    except TelegramForbiddenError:
        return None, models.MessageStatus.FORBIDDEN
    else:
        return message, models.MessageStatus.UPDATED


async def delete(message: models.Message) -> tuple[models.Message | None, models.MessageStatus]:
    await message.delete()

    try:
        await bot.delete_message(message.channel_id, message.message_id)
    except TelegramNotFound:
        return None, models.MessageStatus.NOT_FOUND
    except TelegramForbiddenError:
        return None, models.MessageStatus.FORBIDDEN
    else:
        return message, models.MessageStatus.DELETED
