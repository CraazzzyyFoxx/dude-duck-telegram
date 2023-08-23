from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from beanie import PydanticObjectId

from app.core import config
from app.core.cbdata import OrderRespondConfirmCallback
from app.services.api import service as api_service
from app.services.api import schemas as api_schemas
from app.services.api import flows as api_flows
from app.services.message import service as message_service
from app.services.message import models as message_models
from app.services.render import flows as render_flows
from app.services.pull import models as pull_models

from . import models, service


def get_reply_markup_admin(order_id: PydanticObjectId, user_id: PydanticObjectId) -> InlineKeyboardMarkup:
    blr = InlineKeyboardBuilder()
    b = InlineKeyboardButton(text=f"Approve",
                             callback_data=OrderRespondConfirmCallback(order_id=order_id, user_id=user_id).pack())
    blr.add(b)
    return blr.as_markup()


async def create_response(
        user_id: int,
        order_id: PydanticObjectId,
        data: models.OrderResponseExtra
) -> tuple[int, models.OrderResponse | None]:
    resp = await api_service.request(f'response/{order_id}', 'POST',
                                     await api_service.get_token_user_id(user_id),
                                     json=data.model_dump())
    if resp.status_code == 201:
        return resp.status_code, models.OrderResponse.model_validate(resp.json())
    return resp.status_code, None


async def approve_response(user_id: int, order_id: PydanticObjectId, booster_id: PydanticObjectId) -> int | None:
    order = await api_flows.get_order(user_id, order_id)
    resp = await api_service.request(f'response/{order_id}/{booster_id}/approve', 'GET',
                                     await api_service.get_token_user_id(user_id))
    if resp.status_code in (404, 400, 403, 409):
        return resp.status_code
    messages = await message_service.get_by_order_id_type(order_id, message_models.MessageType.RESPONSE)
    for msg in messages:
        if msg.user_id == booster_id:
            response = await service.get_user_response(user_id, order_id, booster_id)
            _, status = await message_service.update(
                msg,
                message_models.MessageUpdate(
                    text=await render_flows.order(
                        ['base', f"{order.info.game}", 'eta-price', 'response-check'],
                        data={"order": order, "response": response,
                              "user": await api_flows.get_user(user_id, booster_id)}
                    )
                )
            )

        else:
            await message_service.delete(msg)

    return None


async def response_approved(order: api_schemas.Order, user: api_schemas.User,
                            response: models.OrderResponse, **_kwargs):
    users_db = await api_service.get_by_user_id(user.id)
    data = {
        "order": order,
        "resp": response,
        "rendered_order": await render_flows.order(['base', f"{order.info.game}-cd", 'eta-price'],
                                                   data={"order": order})
    }
    resp = []
    for user_db in users_db:
        _, status = await message_service.create(
            message_models.MessageCreate(channel_id=user_db.telegram_user_id,
                                         text=render_flows.user("response_approve", user, data=data),
                                         type=message_models.MessageType.MESSAGE))
        resp.append(pull_models.MessageResponse(status=status, channel_id=user_db.telegram_user_id))
    return pull_models.MessageResponses(statuses=resp)


async def response_declined(order: api_schemas.Order, user: api_schemas.User, **_kwargs):
    users_db = await api_service.get_by_user_id(user.id)
    resp = []
    for user_db in users_db:
        _, status = await message_service.create(
            message_models.MessageCreate(channel_id=user_db.telegram_user_id,
                                         text=render_flows.user("response_decline", user, data={"order": order}),
                                         type=message_models.MessageType.MESSAGE))
        resp.append(pull_models.MessageResponse(status=status, channel_id=user_db.telegram_user_id))
    return pull_models.MessageResponses(statuses=resp)


async def response_to_admins(order: api_schemas.Order, user: api_schemas.User, response: models.OrderResponse):
    _, status = await message_service.create(
        message_models.MessageCreate(
            order_id=order.id,
            user_id=user.id,
            channel_id=config.app.admin_order,
            text=await render_flows.order(
                ['base', f"{order.info.game}", "eta-price", "response"],
                data={"order": order, "response": response, "user": user}
            ),
            reply_markup=get_reply_markup_admin(order.id, user.id),
            type=message_models.MessageType.RESPONSE)
    )

    # if status.FORBIDDEN:
    #     raise RuntimeError("Unable to send a message to the chat room for administrator")
