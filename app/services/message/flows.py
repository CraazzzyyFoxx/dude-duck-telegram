from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core.cbdata import OrderRespondCallback, OrderRespondTimedCallback
from app.services.api import schemas as api_schemas
from app.services.channel import service as channel_service
from app.services.message import models as message_models
from app.services.message import service as message_service
from app.services.render import flows as render_flows

from . import models


def get_reply_markup_instantly(order_id: str) -> InlineKeyboardMarkup:
    blr = InlineKeyboardBuilder()
    for i in range(1, 5):
        b = OrderRespondTimedCallback(order_id=order_id, time=i * 900).pack()
        blr.add(InlineKeyboardButton(text=f"{i * 15} min", callback_data=b))
    blr.adjust(3)
    return blr.as_markup()


def get_reply_markup_response(order_id: str, *, preorder=False) -> InlineKeyboardMarkup:
    blr = InlineKeyboardBuilder()
    b = OrderRespondCallback(order_id=order_id, preorder=preorder).pack()
    blr.add(InlineKeyboardButton(text="I want this order", callback_data=b))
    return blr.as_markup()


async def generate_body(order, configs: list[str], preorder: bool) -> tuple[bool, str]:
    status, missing = await render_flows.check_availability_all_render_config_order(order)
    if not status:
        return status, f"Some configs for order missing, configs=[{', '.join(missing)}]"
    if not configs:
        configs = render_flows.get_order_configs(order, pre=preorder)
    text = await render_flows.order(configs, data={"order": order})
    return status, text


async def pull_create(
    order: api_schemas.Order | api_schemas.PreOrder,
    categories: list[str],
    configs: list[str],
    preorder: bool,
    **_kwargs,
) -> models.OrderResponse:
    chs_id = [ch.channel_id for ch in await channel_service.get_by_game_categories(order.info.game, categories)]
    if not chs_id:
        return models.OrderResponse(error=True, error_msg="A channels with this game do not exist")
    created, skipped = [], []
    status, text = await generate_body(order, configs, preorder)
    if not status:
        return models.OrderResponse(error=True, error_msg=text)
    markup = get_reply_markup_response(order.id, preorder=preorder)
    message_type = message_models.MessageType.ORDER if not preorder else message_models.MessageType.PRE_ORDER
    for channel_id in chs_id:
        msg_in = message_models.MessageCreate(
            order_id=order.id, channel_id=channel_id, text=text, reply_markup=markup, type=message_type
        )
        msg, status = await message_service.create(msg_in)
        if not msg:
            skipped.append(models.SkippedPull(channel_id=channel_id, status=status))
        else:
            created.append(models.SuccessPull(channel_id=channel_id, message_id=msg.message_id, status=status))
    return models.OrderResponse(created=created, skipped=skipped)


async def pull_update(
    order: api_schemas.Order | api_schemas.PreOrder, configs: list[str], preorder: bool, **_kwargs
) -> models.OrderResponse:
    msgs = await message_service.get_by_order_id(order.id, preorder)
    status, text = await generate_body(order, configs, preorder)
    if not status:
        return models.OrderResponse(error=True, error_msg=text)
    updated, skipped = [], []
    for msg in msgs:
        msg_in = message_models.MessageUpdate(
            text=text, inline_keyboard=get_reply_markup_response(order.id, preorder=preorder)
        )
        message, status = await message_service.update(msg, msg_in)
        if not message:
            skipped.append(models.SkippedPull(status=status, channel_id=msg.channel_id))
        else:
            updated.append(models.SuccessPull(channel_id=msg.channel_id, message_id=msg.message_id, status=status))
    return models.OrderResponse(updated=updated, skipped=skipped)


async def pull_delete(
    order: api_schemas.Order | api_schemas.PreOrder, preorder: bool, **_kwargs
) -> models.OrderResponse:
    msgs = await message_service.get_by_order_id(order.id, preorder)
    deleted, skipped = [], []
    for msg in msgs:
        message, status = await message_service.delete(msg)
        if not message:
            skipped.append(models.SkippedPull(status=status, channel_id=msg.channel_id))
        else:
            deleted.append(models.SuccessPull(channel_id=msg.channel_id, message_id=msg.message_id, status=status))
    return models.OrderResponse(deleted=deleted, skipped=skipped)
