from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.core import config
from src.core.cbdata import OrderRespondConfirmCallback
from src.services.api import schemas as api_schemas
from src.services.api import service as api_service
from src.services.message import models as message_models
from src.services.message import service as message_service
from src.services.render import flows as render_flows

from . import models


def get_reply_markup_admin(order_id: int, user_id: int, preorder: bool) -> InlineKeyboardMarkup:
    blr = InlineKeyboardBuilder()
    cb_data = OrderRespondConfirmCallback(order_id=order_id, user_id=user_id, preorder=preorder)
    b = InlineKeyboardButton(text="Approve", callback_data=cb_data.pack())
    blr.add(b)
    return blr.as_markup()


async def create_response(
    user_id: int, order_id: int, data: models.OrderResponseExtra, pre: bool = False
) -> tuple[int, models.OrderResponse | None]:
    resp = await api_service.request(
        f"response?order_id={order_id}&is_preorder={pre}",
        "POST",
        await api_service.get_token_user_id(user_id),
        json=data.model_dump(),
    )
    if resp.status_code == 201:
        return resp.status_code, models.OrderResponse.model_validate(resp.json())
    return resp.status_code, None


async def approve_response(user_id: int, order_id: int, booster_id: int, preorder: bool) -> int:
    resp = await api_service.request(
        f"response/{order_id}/{booster_id}?approve=true&is_preorder={preorder}",
        "PATCH",
        await api_service.get_token_user_id(user_id),
    )
    if resp.status_code in (404, 400, 403, 409):
        return resp.status_code
    for msg in await message_service.get_by_order_id_type(order_id, message_models.MessageType.RESPONSE):
        if msg.user_id == booster_id:
            text = await render_flows.get_order_text(
                user_id, order_id, with_response=True, response_checked=True, response_user_id=booster_id
            )
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
    order: api_schemas.OrderRead, user: api_schemas.User, response: models.OrderResponse, text: str
) -> list[message_models.MessageResponse]:
    users_db = await api_service.get_by_user_id(user.id)
    data = {"order": order, "resp": response}
    order_text = render_flows.user("response_approved", user, data=data)
    order_text = order_text.format(rendered_order=text)
    return [await send_response(user_db.telegram_user_id, order_text) for user_db in users_db]


async def response_declined(
    user: api_schemas.User,
    order_id: int,
) -> list[message_models.MessageResponse]:
    users_db = await api_service.get_by_user_id(user.id)
    text = render_flows.user("response_declined", user, data={"order_id": order_id})
    return [await send_response(user_db.telegram_user_id, text) for user_db in users_db]


async def response_to_admins(
    order: api_schemas.Order,
    preorder: api_schemas.PreOrder,
    user: api_schemas.User,
    text: str,
    is_preorder: bool,
) -> message_models.MessageResponse:
    order_rv = order if not is_preorder else preorder

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
