from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from loguru import logger

from app.core import config
from app.core.cbdata import OrderRespondConfirmCallback
from app.services.api import flows as api_flows
from app.services.api import schemas as api_schemas
from app.services.api import service as api_service
from app.services.message import models as message_models
from app.services.message import service as message_service
from app.services.render import flows as render_flows

from . import models


def get_reply_markup_admin(order_id: int, user_id: int, preorder: bool) -> InlineKeyboardMarkup:
    blr = InlineKeyboardBuilder()
    cb_data = OrderRespondConfirmCallback(order_id=order_id, user_id=user_id, preorder=preorder)
    b = InlineKeyboardButton(text="Approve", callback_data=cb_data.pack())
    blr.add(b)
    return blr.as_markup()


async def create_response(
    user_id: int, order_id: int, data: models.OrderResponseExtra
) -> tuple[int, models.OrderResponse | None]:
    resp = await api_service.request(
        f"response/{order_id}", "POST", await api_service.get_token_user_id(user_id), json=data.model_dump()
    )
    if resp.status_code == 201:
        return resp.status_code, models.OrderResponse.model_validate(resp.json())
    return resp.status_code, None


async def create_preorder_response(
    user_id: int, order_id: int, data: models.OrderResponseExtra
) -> tuple[int, models.OrderResponse | None]:
    resp = await api_service.request(
        f"response/preorder/{order_id}", "POST", await api_service.get_token_user_id(user_id), json=data.model_dump()
    )
    if resp.status_code == 201:
        return resp.status_code, models.OrderResponse.model_validate(resp.json())
    return resp.status_code, None


async def approve_response(user_id: int, order_id: int, booster_id: int, preorder: bool) -> int:
    if preorder:
        url = f"response/preorder/{order_id}/{booster_id}/approve"
        order = await api_flows.get_preorder(user_id, order_id)
    else:
        url = f"response/{order_id}/{booster_id}/approve"
        order = await api_flows.get_order(user_id, order_id)
    resp = await api_service.request(url, "GET", await api_service.get_token_user_id(user_id))
    if resp.status_code in (404, 400, 403, 409):
        return resp.status_code
    for msg in await message_service.get_by_order_id_type(order_id, message_models.MessageType.RESPONSE):
        if msg.user_id == booster_id:
            response = models.OrderResponse.model_validate(resp.json())
            configs = render_flows.get_order_response_configs(order, pre=preorder, checked=True)
            booster = await api_flows.get_user(user_id, booster_id)
            logger.warning(booster)
            text = await render_flows.order(configs, data={"order": order, "response": response, "user": booster})
            _, status = await message_service.update(msg, message_models.MessageUpdate(text=text))
        else:
            await message_service.delete(msg)
    return 200


async def send_response(channel_id: int, text: str) -> message_models.MessageResponse:
    _, status = await message_service.create(
        message_models.MessageCreate(channel_id=channel_id, text=text, type=message_models.MessageType.MESSAGE)
    )
    return message_models.MessageResponse(status=status, channel_id=channel_id)


async def response_approved(
    order: api_schemas.OrderRead,
    user: api_schemas.User,
    response: models.OrderResponse,
) -> list[message_models.MessageResponse]:
    users_db = await api_service.get_by_user_id(user.id)
    configs = render_flows.get_order_configs(order, creds=True)
    rendered_order = await render_flows.pre_rendered_order(configs, data={"order": order})
    data = {"order": order, "resp": response, "rendered_order": rendered_order}
    text = render_flows.user("response_approved", user, data=data)
    return [await send_response(user_db.telegram_user_id, text) for user_db in users_db]


async def response_declined(
    order_id: int,
    user: api_schemas.User,
) -> list[message_models.MessageResponse]:
    users_db = await api_service.get_by_user_id(user.id)
    text = render_flows.user("response_declined", user, data={"order_id": order_id})
    return [await send_response(user_db.telegram_user_id, text) for user_db in users_db]


async def response_to_admins(
    order: api_schemas.Order,
    preorder: api_schemas.PreOrder,
    user: api_schemas.User,
    response: models.OrderResponse,
    is_preorder: bool,
) -> message_models.MessageResponse:
    order_rv = order if not is_preorder else preorder

    configs = render_flows.get_order_response_configs(order_rv, pre=is_preorder, checked=False)
    text = await render_flows.order(configs, data={"order": order_rv, "response": response, "user": user})
    message = await message_service.get_by_order_id_user_id(order_rv.id, user.id)
    if message:
        await message_service.delete(message)

    msg, status = await message_service.create(
        message_models.MessageCreate(
            order_id=order_rv.id if not is_preorder else preorder.id,
            user_id=user.id,
            channel_id=config.app.admin_order,
            text=text,
            reply_markup=get_reply_markup_admin(order_rv.id if not is_preorder else preorder.id, user.id, is_preorder),
            type=message_models.MessageType.RESPONSE,
        )
    )

    return message_models.MessageResponse(status=status, channel_id=msg.channel_id)
