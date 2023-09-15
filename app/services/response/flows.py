from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.core import config
from app.core.cbdata import OrderRespondConfirmCallback
from app.services.api import flows as api_flows
from app.services.api import schemas as api_schemas
from app.services.api import service as api_service
from app.services.message import models as message_models
from app.services.message import service as message_service
from app.services.pull import models as pull_models
from app.services.render import flows as render_flows

from . import models, service


def get_reply_markup_admin(
        order_id: str,
        user_id: str,
        preorder: bool
) -> InlineKeyboardMarkup:
    blr = InlineKeyboardBuilder()
    cb_data = OrderRespondConfirmCallback(order_id=order_id, user_id=user_id, preorder=preorder)
    b = InlineKeyboardButton(text="Approve", callback_data=cb_data.pack())
    blr.add(b)
    return blr.as_markup()


async def create_response(
        user_id: int,
        order_id: str,
        data: models.OrderResponseExtra
) -> tuple[int, models.OrderResponse | None]:
    resp = await api_service.request(f'response/{order_id}', 'POST',
                                     await api_service.get_token_user_id(user_id),
                                     json=data.model_dump())
    if resp.status_code == 201:
        return resp.status_code, models.OrderResponse.model_validate(resp.json())
    return resp.status_code, None


async def create_preorder_response(
        user_id: int,
        order_id: str,
        data: models.OrderResponseExtra
) -> tuple[int, models.OrderResponse | None]:
    resp = await api_service.request(f'response/preorder/{order_id}', 'POST',
                                     await api_service.get_token_user_id(user_id),
                                     json=data.model_dump())
    if resp.status_code == 201:
        return resp.status_code, models.OrderResponse.model_validate(resp.json())
    return resp.status_code, None


async def approve_response(
        user_id: int,
        order_id: str,
        booster_id: str,
        preorder: bool
) -> int | None:
    if preorder:
        url = f"response/preorder/{order_id}/{booster_id}/approve"
        order = await api_flows.get_preorder(user_id, order_id)
    else:
        url = f"response/{order_id}/{booster_id}/approve"
        order = await api_flows.get_order(user_id, order_id)
    resp = await api_service.request(url, 'GET', await api_service.get_token_user_id(user_id))
    if resp.status_code in (404, 400, 403, 409):
        return resp.status_code
    messages = await message_service.get_by_order_id_type(order_id, message_models.MessageType.RESPONSE)
    for msg in messages:
        if msg.user_id == booster_id:
            response = await service.get_user_response(user_id, order_id, booster_id)
            if not preorder:
                configs = render_flows.get_order_response_configs(order, checked=True)
            else:
                configs = render_flows.get_preorder_response_configs(order, checked=True)
            booster = await api_flows.get_user(user_id, booster_id)
            text = await render_flows.order(configs, data={"order": order, "response": response, "user": booster})
            _, status = await message_service.update(msg, message_models.MessageUpdate(text=text))
        else:
            await message_service.delete(msg)

    return None


async def send_response(
        channel_id: int,
        text: str
):
    _, status = await message_service.create(
        message_models.MessageCreate(
            channel_id=channel_id, text=text, type=message_models.MessageType.MESSAGE
        )
    )
    return pull_models.MessageResponse(status=status, channel_id=channel_id)


async def response_approved(
        order: api_schemas.OrderRead,
        user: api_schemas.User,
        response: models.OrderResponse,
        **_kwargs
):
    users_db = await api_service.get_by_user_id(user.id)
    configs = render_flows.get_order_configs(order, creds=True)
    rendered_order = await render_flows._order(configs, data={"order": order})
    data = {"order": order, "resp": response, "rendered_order": rendered_order}
    text = render_flows.user("response_approved", user, data=data)
    resp = []
    for user_db in users_db:
        resp.append(await send_response(user_db.telegram_user_id, text))
    return pull_models.MessageResponses(statuses=resp)


async def response_declined(
        order_id: str,
        user: api_schemas.User,
        **_kwargs
):
    users_db = await api_service.get_by_user_id(user.id)
    text = render_flows.user("response_declined", user, data={"order_id": order_id})
    resp = []
    for user_db in users_db:
        resp.append(await send_response(user_db.telegram_user_id, text))
    return pull_models.MessageResponses(statuses=resp)


async def response_to_admins(
        order: api_schemas.Order,
        preorder: api_schemas.PreOrder,
        user: api_schemas.User,
        response: models.OrderResponse,
        is_preorder: bool
):
    if is_preorder:
        configs = render_flows.get_preorder_response_configs(preorder, checked=False)
        text = await render_flows.order(configs, data={"order": preorder, "response": response, "user": user})
        message = await message_service.get_by_order_id_user_id(preorder.id, user.id)
    else:
        configs = render_flows.get_order_response_configs(order, checked=False)
        text = await render_flows.order(configs, data={"order": order, "response": response, "user": user})
        message = await message_service.get_by_order_id_user_id(order.id, user.id)

    if message:
        await message_service.delete(message)

    _, status = await message_service.create(
        message_models.MessageCreate(
            order_id=order.id if not is_preorder else preorder.id,
            user_id=user.id,
            channel_id=config.app.admin_order,
            text=text,
            reply_markup=get_reply_markup_admin(order.id if not is_preorder else preorder.id, user.id, is_preorder),
            type=message_models.MessageType.RESPONSE)
    )
