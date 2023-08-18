from aiogram.exceptions import TelegramForbiddenError
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from beanie import PydanticObjectId
from fastapi import HTTPException
from starlette import status

from app.core import config
from app.core.bot import bot
from app.core.cbdata import OrderRespondConfirmCallback
from app.services.api import service as api_service
from app.services.api import schemas as api_schemas
from app.services.api import flows as api_flows
from app.services.render import flows as render_flows
from app.services.render import service as render_service
from app.utils.templates import render_template_system, render_template_user
from app.utils.helpers import try_message

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
) -> models.OrderResponseAPI | int:
    resp = await api_service.request(f'response/{order_id}', 'POST',
                                     await api_service.get_token_user_id(user_id),
                                     json=data.model_dump())
    if resp.status_code == 201:
        return models.OrderResponseAPI.model_validate(resp.json())
    return resp.status_code


async def approve_response(user_id: int, order_id: PydanticObjectId, booster_id: PydanticObjectId):
    order = await api_flows.get_order(user_id, order_id)
    configs = await render_service.get_by_names(['base', f"{order.game}", 'eta-price', 'resp-admin'])
    resp = await api_service.request(f'response/{order_id}/{booster_id}/approve', 'GET',
                                     await api_service.get_token_user_id(user_id))
    if resp.status_code == 404:
        await bot.send_message(user_id, render_template_system("response_approve_404"))
        return
    responses = await service.get_by_order_id(order_id)
    for resp in responses:
        if resp.user_id == booster_id:
            response = await get_user_response(user_id, order_id, booster_id)
            text = render_flows.render_order(order, configs, response=response)
            async with try_message():
                await bot.edit_message_text(render_template_system("order", data={"rendered_order": text}),
                                            chat_id=resp.channel_id,
                                            message_id=resp.message_id)
        else:
            await bot.delete_message(resp.channel_id, resp.message_id)
        await service.delete(resp.id)


async def get_me_response(user_id: int, order_id: PydanticObjectId):
    resp = await api_service.request(f'response/{order_id}/@me', 'GET', await api_service.get_token_user_id(user_id))
    if resp.status_code == 200:
        return models.OrderResponseAPI.model_validate(resp.json())


async def get_user_response(user_id: int, order_id: PydanticObjectId, booster_id: PydanticObjectId):
    resp = await api_service.request(f'response/{order_id}/{booster_id}', 'GET',
                                     await api_service.get_token_user_id(user_id))
    if resp.status_code == 200:
        return models.OrderResponseAPI.model_validate(resp.json())


async def get_order_responses(user_id: int, order_id: PydanticObjectId):
    resp = await api_service.request(f'response/{order_id}/@me', 'GET',
                                     await api_service.get_token_user_id(user_id))
    return [models.OrderResponseAPI.model_validate(r) for r in resp.json()]


async def response_approved(order: api_schemas.Order, user: api_schemas.User,
                            response: models.OrderResponseAPI, **_kwargs):
    configs = await render_service.get_by_names(['base', f"{order.game}-cd", 'eta-price'])
    data = {"order": order, "resp": response, "rendered_order": render_flows.render_order(order=order, configs=configs)}
    user_db = await api_service.get(user.id)
    try:
        await bot.send_message(user_db.telegram_user_id, render_template_user("response_approve", user, data=data))
    except TelegramForbiddenError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=[{"msg": "The bot cannot contact the user"}])


async def response_declined(order: api_schemas.Order, user: api_schemas.User, **_kwargs):
    user_db = await api_service.get(user.id)
    data = {"order": order}
    try:
        await bot.send_message(user_db.telegram_user_id, render_template_user("response_decline", user, data=data))
    except TelegramForbiddenError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=[{"msg": "The bot cannot contact the user"}])


async def response_to_admins(order: api_schemas.Order, user: api_schemas.User, response: models.OrderResponseAPI):
    configs = await render_flows.get_base_respond_names(order)
    text = render_flows.render_order(order, configs, response=response)
    try:
        msg = await bot.send_message(config.app.admin_order,
                                     render_template_system("response_admins", data={"rendered_order": text}),
                                     reply_markup=get_reply_markup_admin(order.id, user.id))
        resp = await service.create(
            models.OrderResponseCreate(
                order_id=order.id,
                user_id=user.id,
                channel_id=msg.chat.id,
                message_id=msg.message_id
            )
        )
        return  # TODO:
    except TelegramForbiddenError:
        raise RuntimeError("Unable to send a message to the chat room for administrator")
