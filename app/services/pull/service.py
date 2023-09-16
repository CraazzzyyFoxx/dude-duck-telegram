from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core import config
from app.core.cbdata import OrderRespondCallback, OrderRespondTimedCallback
from app.services.api import flows as api_flows
from app.services.api import schemas as api_schemas
from app.services.api import service as api_service
from app.services.api import models as api_models
from app.services.channel import service as channel_service
from app.services.message import models as message_models
from app.services.message import service as message_service
from app.services.render import flows as render_flows
from app.services.response import flows as response_flows

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
        configs = render_flows.get_order_configs(order) if not preorder else render_flows.get_preorder_configs(order)
    text = await render_flows.order(configs, data={"order": order})
    return status, text


async def pull_create(
        order: api_schemas.Order | api_schemas.PreOrder,
        categories: list[str],
        configs: list[str],
        preorder: bool,
        **_kwargs
) -> models.OrderResponse:
    chs_id = [ch.channel_id for ch in await channel_service.get_by_game_categories(order.info.game, categories)]
    # if not chs_id:
    #     if channel := await channel_service.get_by_game_category(order.info.game, None):
    #         chs_id.append(channel.channel_id)
    if not chs_id:
        return models.OrderResponse(error=True, error_msg="A channels with this game do not exist")
    created, skipped = [], []
    status, text = await generate_body(order, configs, preorder)
    if not status:
        return models.OrderResponse(error=True, error_msg=text)
    markup = get_reply_markup_response(order.id, preorder=preorder)
    message_type = message_models.MessageType.ORDER if not preorder else message_models.MessageType.PRE_ORDER
    for channel_id in chs_id:
        msg_in = message_models.MessageCreate(order_id=order.id, channel_id=channel_id, text=text, reply_markup=markup,
                                              type=message_type)
        msg, status = await message_service.create(msg_in)
        if not msg:
            skipped.append(models.SkippedPull(channel_id=channel_id, status=status))
        else:
            created.append(models.SuccessPull(channel_id=channel_id, message_id=msg.message_id, status=status))
    return models.OrderResponse(created=created, skipped=skipped)


async def pull_update(
        order: api_schemas.Order | api_schemas.PreOrder,
        configs: list[str],
        preorder: bool,
        **_kwargs
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
        order: api_schemas.Order | api_schemas.PreOrder,
        preorder: bool,
        **_kwargs
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


async def pull_order_create(
        order: api_schemas.Order,
        categories: list[str],
        configs: list[str],
        **_kwargs
) -> models.OrderResponse:
    return await pull_create(order, categories, configs, False)


async def pull_order_update(
        order: api_schemas.Order,
        configs: list[str],
        **_kwargs
) -> models.OrderResponse:
    return await pull_update(order, configs, False)


async def pull_order_delete(
        order: api_schemas.Order,
        **_kwargs
) -> models.OrderResponse:
    return await pull_delete(order, False)


async def pull_preorder_create(
        preorder: api_schemas.PreOrder,
        categories: list[str],
        configs: list[str],
        **_kwargs
) -> models.OrderResponse:
    return await pull_create(preorder, categories, configs, True)


async def pull_preorder_update(
        preorder: api_schemas.PreOrder,
        configs: list[str],
        **_kwargs
) -> models.OrderResponse:
    return await pull_update(preorder, configs, True)


async def pull_preorder_delete(
        preorder: api_schemas.PreOrder,
        **_kwargs
) -> models.OrderResponse:
    return await pull_delete(preorder, True)


async def pull_order_admins(
        order: api_schemas.Order,
        preorder: api_schemas.PreOrder,
        user: api_schemas.User,
        response: response_flows.models.OrderResponse,
        is_preorder: bool,
        **_kwargs
):
    return await response_flows.response_to_admins(order, preorder, user, response, is_preorder)


async def pull_booster_resp_yes(
        order_id: str,
        user: api_schemas.User,
        response: response_flows.models.OrderResponse,
        **_kwargs
):
    tg_user = await api_service.get_by_user_id(user.id)
    order = await api_flows.get_me_order(tg_user[0].telegram_user_id, order_id)
    return await response_flows.response_approved(order, user, response)


async def pull_booster_resp_no(
        order_id: str,
        user: api_schemas.User,
        **_kwargs
):
    return await response_flows.response_declined(order_id, user)


async def send_request_verify(
        user: api_schemas.User,
        token: str,
        **_kwargs
):
    data = {"user": user, "token": token}
    _, status = await message_service.create(message_models.MessageCreate(
        text=render_flows.system("notify_verify", data=data),
        channel_id=config.app.admin_important_events,
        type=message_models.MessageType.MESSAGE)
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_important_events)


async def send_verified(
        user: api_schemas.User,
        **_kwargs
):
    resp = []

    users_db = await api_service.get_by_user_id(user.id)
    for user_db in users_db:
        await api_service.update(user_db, api_models.TelegramUserUpdate(user=user))
        _, status = await message_service.create(message_models.MessageCreate(
            text=render_flows.user("verified", user),
            channel_id=user_db.telegram_user_id,
            type=message_models.MessageType.MESSAGE)
        )
        resp.append(models.MessageResponse(status=status, channel_id=config.app.admin_important_events))
    return resp


async def send_order_close_request(
        user: api_schemas.User,
        order_id: str,
        url: str,
        message: str,
        **_kwargs
):
    data = {"user": user, "order_id": order_id, "url": url, "message": message}
    _, status = await message_service.create(message_models.MessageCreate(
        text=render_flows.system("notify_order_close", data=data),
        channel_id=config.app.admin_important_events,
        type=message_models.MessageType.MESSAGE)
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_important_events)


async def send_logged_notify(
        user: api_schemas.User,
        **_kwargs
):
    data = {"user": user}
    _, status = await message_service.create(message_models.MessageCreate(
        text=render_flows.system("notify_logged", data=data),
        channel_id=config.app.admin_events,
        type=message_models.MessageType.MESSAGE)
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_events)


async def send_registered_notify(
        user: api_schemas.User,
        **_kwargs
):
    data = {"user": user}
    _, status = await message_service.create(message_models.MessageCreate(
        text=render_flows.system("notify_registered", data=data),
        channel_id=config.app.admin_important_events,
        type=message_models.MessageType.MESSAGE)
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_important_events)


async def send_order_sent_notify(
        order_id: str,
        pull_payload,
        **_kwargs
):
    data = {"order_id": order_id, "payload": pull_payload}
    _, status = await message_service.create(message_models.MessageCreate(
        text=render_flows.system("notify_order_sent", data=data),
        channel_id=config.app.admin_noise_events,
        type=message_models.MessageType.MESSAGE)
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_noise_events)


async def send_order_edited_notify(
        order_id: str,
        pull_payload,
        **_kwargs
):
    data = {"order_id": order_id, "payload": pull_payload}
    _, status = await message_service.create(message_models.MessageCreate(
        text=render_flows.system("notify_order_edited", data=data),
        channel_id=config.app.admin_noise_events,
        type=message_models.MessageType.MESSAGE)
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_noise_events)


async def send_order_deleted_notify(
        order_id: str,
        pull_payload,
        **_kwargs
):
    data = {"order_id": order_id, "payload": pull_payload}
    _, status = await message_service.create(message_models.MessageCreate(
        text=render_flows.system("notify_order_deleted", data=data),
        channel_id=config.app.admin_noise_events,
        type=message_models.MessageType.MESSAGE)
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_noise_events)


async def send_response_chose_notify(
        order_id: str,
        responses: int,
        user: api_schemas.User,
        **_kwargs
):
    data = {"order_id": order_id, "total": responses, "user": user}
    _, status = await message_service.create(message_models.MessageCreate(
        text=render_flows.system("notify_response_chose", data=data),
        channel_id=config.app.admin_events,
        type=message_models.MessageType.MESSAGE)
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_events)


async def send_order_paid_notify(
        order,
        user,
        **_kwargs
):
    data = {"order": order, "user": user}
    _, status = await message_service.create(message_models.MessageCreate(
        text=render_flows.system("notify_order_paid", data=data),
        channel_id=config.app.admin_events,
        type=message_models.MessageType.MESSAGE)
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_events)
