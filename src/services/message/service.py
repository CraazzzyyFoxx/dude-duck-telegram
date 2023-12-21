import sqlalchemy as sa
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramNotFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.bot import bot
from src import models



async def get(session: AsyncSession, message_id: int) -> models.Message | None:
    query = sa.select(models.Message).where(models.Message.id == message_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_by_order_id_user_id(session: AsyncSession, order_id: int, user_id: int) -> models.Message | None:
    query = sa.select(models.Message).where(models.Message.order_id == order_id, models.Message.user_id == user_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def get_by_order_id_type(
    session: AsyncSession, order_id: int, message_type: models.MessageType
) -> list[models.Message]:
    query = sa.select(models.Message).where(models.Message.order_id == order_id, models.Message.type == message_type)
    result = await session.execute(query)
    return result.scalars().all()  # type: ignore


async def get_by_channel_id_message_id(session: AsyncSession, channel_id: int, message_id: int) -> models.Message:
    query = sa.select(models.Message).where(
        models.Message.channel_id == channel_id, models.Message.message_id == message_id
    )
    result = await session.execute(query)
    return result.scalar_one_or_none()


async def _create(session: AsyncSession, message_in: models.MessageCreate):
    try:
        msg = await bot.send_message(message_in.channel_id, message_in.text, reply_markup=message_in.reply_markup)
    except TelegramForbiddenError:
        return None, models.CallbackStatus.FORBIDDEN

    message_db = models.Message(
        message_id=msg.message_id,
        **message_in.model_dump(exclude_unset=True, exclude_none=True, exclude={"text", "reply_markup"}),
    )
    session.add(message_db)
    await session.commit()
    return message_db, models.CallbackStatus.CREATED


async def create_order(
    session: AsyncSession, message_in: models.MessageCreate
) -> tuple[models.Message | None, models.CallbackStatus]:
    messages = await get_by_order_id_type(session, message_in.order_id, message_in.type)
    channels_id = [msg.channel_id for msg in messages]
    if message_in.channel_id not in channels_id:
        return await _create(session, message_in)
    return None, models.CallbackStatus.EXISTS


async def create_response(
    session: AsyncSession, message_in: models.MessageCreate
) -> tuple[models.Message | None, models.CallbackStatus]:
    message = await get_by_order_id_user_id(session, message_in.order_id, message_in.user_id)
    if message is None:
        return await _create(session, message_in)
    return None, models.CallbackStatus.EXISTS


async def create(
    session: AsyncSession, message_in: models.MessageCreate
) -> tuple[models.Message | None, models.CallbackStatus]:
    if message_in.type == models.MessageType.ORDER:
        return await create_order(session, message_in)
    elif message_in.type == models.MessageType.PRE_ORDER:
        return await create_order(session, message_in)
    elif message_in.type == models.MessageType.RESPONSE:
        return await create_response(session, message_in)

    return await _create(session, message_in)


async def update(
    session: AsyncSession, message: models.Message, message_in: models.MessageUpdate
) -> tuple[models.Message | None, models.CallbackStatus]:
    try:
        if message_in.text is None and message_in.inline_keyboard is None:
            await bot.edit_message_reply_markup(
                message.channel_id,
                message.message_id,
                reply_markup=message_in.inline_keyboard,
            )
        else:
            await bot.edit_message_text(
                message_in.text,
                message.channel_id,
                message.message_id,
                reply_markup=message_in.inline_keyboard,
            )
    except TelegramBadRequest:
        return None, models.CallbackStatus.SAME_TEXT
    except TelegramNotFound:
        await session.delete(message)
        await session.commit()
        return None, models.CallbackStatus.NOT_FOUND
    except TelegramForbiddenError:
        return None, models.CallbackStatus.FORBIDDEN
    else:
        return message, models.CallbackStatus.UPDATED


async def delete(session: AsyncSession, message: models.Message) -> tuple[models.Message | None, models.CallbackStatus]:
    await session.delete(message)
    await session.commit()

    try:
        await bot.delete_message(message.channel_id, message.message_id)
    except TelegramBadRequest:
        return None, models.CallbackStatus.NOT_FOUND
    except TelegramForbiddenError:
        return None, models.CallbackStatus.FORBIDDEN
    else:
        return message, models.CallbackStatus.DELETED
