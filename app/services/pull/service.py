from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from beanie import PydanticObjectId
from fastapi import HTTPException

from app.core import config
from app.core.cbdata import OrderRespondTimedCallback, OrderRespondCallback
from app.services.api import schemas as api_schemas
from app.services.response import flows as response_flows
from app.services.message import service as message_service
from app.services.channel import service as channel_service
from app.services.message import models as message_models
from app.services.render import flows as render_flows

from . import models


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
) -> models.OrderResponse:
    channels_id = [ch.channel_id
                   for ch in await channel_service.get_channels_by_game_categories(order.info.game, categories)]

    if not channels_id:
        if channel := await channel_service.get_channel_by_game_category(order.info.game, None):
            channels_id.append(channel.channel_id)
        else:
            raise HTTPException(status_code=404, detail=[{"msg": "A channels with this game do not exist"}])
    await render_flows.check_availability_all_render_config_order(order)

    created = []
    skipped = []
    for channel_id in channels_id:
        msg, status = await message_service.create(
            message_models.MessageCreate(order_id=order.id,
                                         channel_id=channel_id,
                                         text=await render_flows.order(configs, data={"order": order}),
                                         type=message_models.MessageType.ORDER,
                                         reply_markup=get_reply_markup_response(order.id)))
        if not msg:
            skipped.append(models.SkippedPull(status=status, channel_id=channel_id))
        else:
            created.append(models.SuccessPull(channel_id=channel_id, message_id=msg.message_id, status=status))

    return models.OrderResponse(created=created, skipped=skipped)


async def pull_update(order: api_schemas.Order, configs: list[str], **_kwargs):
    msgs = await message_service.get_by_order_id(order.id)
    await render_flows.check_availability_all_render_config_order(order)
    updated = []
    skipped = []
    for msg in msgs:
        message, status = await message_service.update(
            msg,
            message_models.MessageUpdate(text=await render_flows.order(configs, data={"order": order}),
                                         inline_keyboard=get_reply_markup_response(order.id))
        )
        if not msg:
            skipped.append(models.SkippedPull(status=status, channel_id=msg.channel_id))
        else:
            updated.append(models.SuccessPull(channel_id=msg.channel_id, message_id=msg.message_id, status=status))

    return models.OrderResponse(created=updated, skipped=skipped)


async def pull_delete(order: api_schemas.Order, **_kwargs):
    msgs = await message_service.get_by_order_id(order.id)
    deleted = []
    skipped = []
    for msg in msgs:
        message, status = await message_service.delete(msg)
        if not msg:
            skipped.append(models.SkippedPull(status=status, channel_id=msg.channel_id))
        else:
            deleted.append(models.SuccessPull(channel_id=msg.channel_id, message_id=msg.message_id, status=status))
    return models.OrderResponse(created=deleted, skipped=skipped)


async def pull_admins(order, user, response, **_kwargs):
    return await response_flows.response_to_admins(order, user, response)


async def pull_booster_resp_yes(order, user, response, **_kwargs):
    return await response_flows.response_approved(order, user, response)


async def pull_booster_resp_no(order, user, **_kwargs):
    return await response_flows.response_declined(order, user)


async def send_request_verify(user: api_schemas.User, token: str, **_kwargs):
    data = {"user": user, "token": token}
    _, status = await message_service.create(message_models.MessageCreate(
        text=render_flows.system("notify_verify", data=data),
        channel_id=config.app.admin_important_events,
        type=message_models.MessageType.MESSAGE)
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_important_events)


async def send_verified(user: api_schemas.User, **_kwargs):
    _, status = await message_service.create(message_models.MessageCreate(
        text=render_flows.user("verified", user),
        channel_id=config.app.admin_important_events,
        type=message_models.MessageType.MESSAGE)
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_important_events)


async def send_order_close_request(user, order, url, message, **_kwargs):
    data = {"user": user, "order": order, "url": url, "message": message}
    _, status = await message_service.create(message_models.MessageCreate(
        text=render_flows.system("notify_order_close", data=data),
        channel_id=config.app.admin_important_events,
        type=message_models.MessageType.MESSAGE)
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_important_events)


async def send_logged_notify(user, **_kwargs):
    data = {"user": user}
    _, status = await message_service.create(message_models.MessageCreate(
        text=render_flows.system("notify_logged", data=data),
        channel_id=config.app.admin_events,
        type=message_models.MessageType.MESSAGE)
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_events)


async def send_registered_notify(user, **_kwargs):
    data = {"user": user}
    _, status = await message_service.create(message_models.MessageCreate(
        text=render_flows.system("notify_registered", data=data),
        channel_id=config.app.aadmin_important_events,
        type=message_models.MessageType.MESSAGE)
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_important_events)


async def send_order_sent_notify(order, count_channels, **_kwargs):
    data = {"order": order, "count_channels": count_channels}
    _, status = await message_service.create(message_models.MessageCreate(
        text=render_flows.system("notify_order_sent", data=data),
        channel_id=config.app.admin_noise_events,
        type=message_models.MessageType.MESSAGE)
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_noise_events)


async def send_order_edited_notify(order, count_channels, **_kwargs):
    data = {"order": order, "count_channels": count_channels}
    _, status = await message_service.create(message_models.MessageCreate(
        text=render_flows.system("notify_order_edited", data=data),
        channel_id=config.app.admin_noise_events,
        type=message_models.MessageType.MESSAGE)
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_noise_events)


async def send_order_deleted_notify(order, count_channels, **_kwargs):
    data = {"order": order, "count_channels": count_channels}
    _, status = await message_service.create(message_models.MessageCreate(
        text=render_flows.system("notify_order_deleted", data=data),
        channel_id=config.app.admin_noise_events,
        type=message_models.MessageType.MESSAGE)
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_noise_events)


async def send_response_chose_notify(order, total, user, **_kwargs):
    data = {"order": order, "total": total, "user": user}
    _, status = await message_service.create(message_models.MessageCreate(
        text=render_flows.system("notify_response_chose", data=data),
        channel_id=config.app.admin_events,
        type=message_models.MessageType.MESSAGE)
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_events)


async def send_order_paid_notify(order, user, **_kwargs):
    data = {"order": order, "user": user}
    _, status = await message_service.create(message_models.MessageCreate(
        text=render_flows.system("notify_order_paid", data=data),
        channel_id=config.app.admin_events,
        type=message_models.MessageType.MESSAGE)
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_events)
