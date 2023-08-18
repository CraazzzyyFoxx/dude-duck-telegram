from aiogram.exceptions import TelegramForbiddenError
from beanie import PydanticObjectId

from app.core.bot import bot

from . import models


async def get(message_id: PydanticObjectId) -> models.Message | None:
    return await models.Message.find_one({"_id": message_id})


async def get_by_type(message_id: PydanticObjectId, message_type: models.MessageType) -> list[models.Message]:
    return await models.Message.find({"_id": message_id, "type": message_type, "is_deleted": False}).to_list()


async def get_by_order_id(order_id: PydanticObjectId) -> list[models.Message]:
    return await models.Message.find({"order_id": order_id, "is_deleted": False}).to_list()


async def get_by_user_id(user_id: PydanticObjectId) -> list[models.Message]:
    return await models.Message.find({"user_id": user_id, "is_deleted": False}).to_list()


async def get_by_order_id_user_id(order_id: PydanticObjectId, user_id: PydanticObjectId) -> models.Message:
    return await models.Message.find_one({"order_id": order_id, "user_id": user_id, "is_deleted": False})


async def get_by_order_id_type(order_id: PydanticObjectId, message_type: models.MessageType) -> list[models.Message]:
    return await models.Message.find({"order_id": order_id, "type": message_type, "is_deleted": False}).to_list()


async def create_order(message_in: models.MessageCreate) -> models.Message | bool:
    messages = await get_by_order_id_type(message_in.order_id, message_in.type)
    channels_id = [msg.channel_id for msg in messages]
    if message_in.channel_id not in channels_id:
        try:
            msg = await bot.send_message(message_in.channel_id, message_in.text, reply_markup=message_in.reply_markup)
        except TelegramForbiddenError:
            return True
        message_db = models.Message(message_id=msg.message_id,
                                    **message_in.model_dump(exclude_unset=True, exclude_none=True))
        await message_db.create()
        return message_db
    return False


async def create_response(message_in: models.MessageCreate) -> models.Message | bool:
    message = await get_by_order_id_user_id(message_in.order_id, message_in.user_id)
    if message_in.channel_id != message.channel_id:
        try:
            msg = await bot.send_message(message_in.channel_id, message_in.text, reply_markup=message_in.reply_markup)
        except TelegramForbiddenError:
            return True
        message_db = models.Message(message_id=msg.message_id,
                                    **message_in.model_dump(exclude_unset=True, exclude_none=True))
        await message_db.create()
        return message_db
    return False


async def create(message_in: models.MessageCreate) -> models.Message | bool:
    if message_in.type == models.MessageType.ORDER:
        return await create_order(message_in)
    elif message_in.type == models.MessageType.RESPONSE:
        return await create_response(message_in)


async def update(message: models.Message, message_in: models.MessageUpdate):
    message_data = message.model_dump()
    update_data = message_in.model_dump(exclude_none=True)

    for field in message_data:
        if field in update_data:
            setattr(message, field, update_data[field])

    await message.save_changes()
    return message


async def delete(message_id: PydanticObjectId):
    message = await models.Message.get(message_id)
    await message.delete()


async def get_all() -> list[models.Message]:
    return await models.Message.find({}).to_list()


async def get_by_order_id_channel_id(order_id: PydanticObjectId, channel_id: int) -> list[models.Message]:
    return await models.Message.find({"order_id": order_id, "channel_id": channel_id}).to_list()
