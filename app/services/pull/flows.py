from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
from beanie import PydanticObjectId
from fastapi import HTTPException

from app.core import config
from app.core.bot import bot
from app.core.cbdata import OrderRespondTimedCallback, OrderRespondCallback

from app.services.api import schemas as api_schemas
from app.services.response import flows as response_flows
from app.services.render import flows as render_flows
from app.services.render import service as render_service
from app.services.message import service as message_service
from app.services.channel import service as channel_service
from app.services.message import models as message_models

from app.utils.templates import render_template_system, render_template_user

from . import models


async def process_event(event: models.MessageEvent):
    if event.type == models.MessageEnum.SEND_ORDER:
        return await pull_create(**dict(event.payload))
    if event.type == models.MessageEnum.EDIT_ORDER:
        return await pull_update(**dict(event.payload))
    if event.type == models.MessageEnum.DELETE_ORDER:
        return await pull_delete(**dict(event.payload))
    if event.type == models.MessageEnum.RESPONSE_ADMINS:
        return await pull_admins(**dict(event.payload))
    if event.type == models.MessageEnum.RESPONSE_APPROVED:
        return await pull_booster_resp_yes(**dict(event.payload))
    if event.type == models.MessageEnum.RESPONSE_DECLINED:
        return await pull_booster_resp_no(**dict(event.payload))
    if event.type == models.MessageEnum.REQUEST_VERIFY:
        return await pull_request_verify(**dict(event.payload))
    if event.type == models.MessageEnum.VERIFIED:
        return await pull_verified(**dict(event.payload))
    if event.type == models.MessageEnum.REQUEST_CLOSE_ORDER:
        return await pull_order_close_request(**dict(event.payload))


def get_reply_markup_instantly(order_id: PydanticObjectId) -> InlineKeyboardMarkup:
    blr = InlineKeyboardBuilder()
    for i in range(1, 5):
        b = OrderRespondTimedCallback(order_id=order_id, time=i * 900).pack()
        blr.add(InlineKeyboardButton(text=f"{i * 15} min", callback_data=b))
    blr.adjust(3)
    return blr.as_markup()


def get_reply_markup_response(order_id: PydanticObjectId) -> InlineKeyboardMarkup:
    blr = InlineKeyboardBuilder()
    b = OrderRespondCallback(order_id=order_id).pack()
    blr.add(InlineKeyboardButton(text=f"I want this order", callback_data=b))
    return blr.as_markup()


async def pull_create(
        order: api_schemas.Order,
        categories: list[str],
        configs: list[str],
        **_kwargs
) -> dict:
    channels_id = [channel.channel_id
                   for channel in await channel_service.get_channels_by_game_categories(order.info.game, categories)]

    if not channels_id:
        if channel := await channel_service.get_channel_by_game_category(order.info.game, None):
            channels_id.append(channel.channel_id)
        else:
            raise HTTPException(status_code=404, detail=[{"msg": "A channels with this game do not exist"}])

    created = []
    skipped = []
    configs = await render_service.get_by_names(configs)
    text = render_flows.render_order(order=order, configs=configs)
    for channel_id in channels_id:
        msg = await message_service.create(
            message_models.MessageCreate(order_id=order.id,
                                         channel_id=channel_id,
                                         text=render_template_system("order", data={"rendered_order": text}),
                                         type=message_models.MessageType.ORDER,
                                         reply_markup=get_reply_markup_response(order.id)))
        if msg is True or msg is False:
            skipped.append(channel_id)
        else:
            created.append(channel_id)

    return {"created": created, "skipped": skipped}


async def pull_update(order: api_schemas.Order, configs: list[str], **_kwargs) -> list[message_models.Message]:
    msgs = await message_service.get_by_order_id(order.id)
    configs = await render_service.get_by_names(configs)
    r = []
    for msg in msgs:
        text = render_flows.render_order(order=order, configs=configs)
        try:
            await bot.edit_message_text(chat_id=msg.channel_id, message_id=msg.message_id,
                                        text=render_template_system("order", data={"rendered_order": text}),
                                        reply_markup=get_reply_markup_response(order.id))
        except TelegramBadRequest:
            pass  # TODO:
            r.append(msg)
    return r


async def pull_delete(order: api_schemas.Order, **_kwargs) -> list[message_models.Message]:
    msgs = await message_service.get_by_order_id(order.id)
    r = []
    for msg in msgs:
        await msg.delete_message()
        try:
            await bot.delete_message(chat_id=msg.channel_id, message_id=msg.message_id)
        except TelegramBadRequest:
            pass  # TODO:
        r.append(msg)
    return r


async def pull_admins(order, user, response, **_kwargs):
    return await response_flows.response_to_admins(order, user, response)


async def pull_booster_resp_yes(order, user, response, **_kwargs):
    return await response_flows.response_approved(order, user, response)


async def pull_booster_resp_no(order, user, **_kwargs):
    return await response_flows.response_declined(order, user)


async def pull_request_verify(user: api_schemas.User, token: str, **_kwargs):
    data = {"user": user, "token": token}
    await bot.send_message(config.app.admin_events, render_template_system("verify", data=data))


async def pull_verified(user: api_schemas.User, **_kwargs):
    await bot.send_message(config.app.admin_events, render_template_user("verified", user))


async def pull_order_close_request(user, order, url, message, **_kwargs):
    data = {"user": user, "order": order, "url": url, "message": message}
    await bot.send_message(config.app.admin_events,
                           render_template_system("order_close", data=data),
                           disable_web_page_preview=True
                           )
