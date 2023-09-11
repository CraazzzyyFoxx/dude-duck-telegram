from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest, TelegramNotFound
from beanie import PydanticObjectId

from app.core.bot import bot

from . import models


async def get(message_id: PydanticObjectId) -> models.Message | None:
    return await models.Message.find_one({"_id": message_id})


async def get_by_type(message_id: PydanticObjectId, message_type: models.MessageType) -> list[models.Message]:
    return await models.Message.find({"_id": message_id, "type": message_type, "is_deleted": False}).to_list()


async def get_by_order_id(order_id: PydanticObjectId, preorder: bool) -> list[models.Message]:
    message_type = models.MessageType.PRE_ORDER if preorder else models.MessageType.ORDER
    return await models.Message.find({"order_id": order_id, "is_deleted": False, "type": message_type}).to_list()


async def get_by_user_id(user_id: PydanticObjectId) -> list[models.Message]:
    return await models.Message.find({"user_id": user_id, "is_deleted": False}).to_list()


async def get_by_order_id_user_id(order_id: PydanticObjectId, user_id: PydanticObjectId) -> models.Message | None:
    return await models.Message.find_one({"order_id": order_id, "user_id": user_id, "is_deleted": False})


async def get_by_order_id_type(order_id: PydanticObjectId, message_type: models.MessageType) -> list[models.Message]:
    return await models.Message.find({"order_id": order_id, "type": message_type, "is_deleted": False}).to_list()


async def get_by_order_id_channel_id(order_id: PydanticObjectId, channel_id: int) -> list[models.Message]:
    return await models.Message.find({"order_id": order_id, "channel_id": channel_id, "is_deleted": False}).to_list()


async def get_by_channel_id_message_id(channel_id: int, message_id: int) -> models.Message:
    return await models.Message.find_one({"channel_id": channel_id, "message_id": message_id, "is_deleted": False})


async def _create(message_in: models.MessageCreate):
    try:
        msg = await bot.send_message(message_in.channel_id, message_in.text, reply_markup=message_in.reply_markup)
    except TelegramForbiddenError:
        return None, models.MessageStatus.FORBIDDEN
    message_db = models.Message(message_id=msg.message_id,
                                **message_in.model_dump(exclude_unset=True, exclude_none=True))
    await message_db.create()
    return message_db, models.MessageStatus.CREATED


async def create_order(message_in: models.MessageCreate) -> tuple[models.Message | None,  models.MessageStatus]:
    messages = await get_by_order_id_type(message_in.order_id, message_in.type)
    channels_id = [msg.channel_id for msg in messages]
    if message_in.channel_id not in channels_id:
        return await _create(message_in)
    return None, models.MessageStatus.EXISTS


async def create_response(message_in: models.MessageCreate) -> tuple[models.Message | None,  models.MessageStatus]:
    message = await get_by_order_id_user_id(message_in.order_id, message_in.user_id)
    if message is None:
        return await _create(message_in)
    return None, models.MessageStatus.EXISTS


async def create(message_in: models.MessageCreate) -> tuple[models.Message | None,  models.MessageStatus]:
    if message_in.type == models.MessageType.ORDER:
        return await create_order(message_in)
    elif message_in.type == models.MessageType.PRE_ORDER:
        return await create_order(message_in)
    elif message_in.type == models.MessageType.RESPONSE:
        return await create_response(message_in)
    elif message_in.type == models.MessageType.MESSAGE:
        return await _create(message_in)


async def update(
        message: models.Message,
        message_in: models.MessageUpdate
) -> tuple[models.Message | None,  models.MessageStatus]:
    try:
        if message_in.text is None and message_in.inline_keyboard is None:
            await bot.edit_message_reply_markup(
                message.channel_id, message.message_id, reply_markup=message_in.inline_keyboard)
        else:
            await bot.edit_message_text(
                message_in.text, message.channel_id, message.message_id, reply_markup=message_in.inline_keyboard)
    except TelegramBadRequest:
        return None, models.MessageStatus.SAME_TEXT
    except TelegramNotFound:
        return None, models.MessageStatus.NOT_FOUND
    except TelegramForbiddenError:
        return None, models.MessageStatus.FORBIDDEN
    else:
        return message, models.MessageStatus.UPDATED


async def delete(message: models.Message) -> tuple[models.Message | None,  models.MessageStatus]:
    try:
        await bot.delete_message(message.channel_id, message.message_id)
    except TelegramNotFound:
        return None, models.MessageStatus.NOT_FOUND
    except TelegramForbiddenError:
        return None, models.MessageStatus.FORBIDDEN
    else:
        message.is_deleted = True
        await message.save()
        return message, models.MessageStatus.DELETED