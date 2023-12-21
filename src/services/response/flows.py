from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import config
from src import models, schemas
from src.core.cbdata import OrderRespondConfirmCallback
from src.services.api import service as api_service
from src.services.message import service as message_service
from src.services.render import flows as render_flows


def get_reply_markup_admin(order_id: int, user_id: int, preorder: bool) -> InlineKeyboardMarkup:
    blr = InlineKeyboardBuilder()
    cb_data_true = OrderRespondConfirmCallback(order_id=order_id, user_id=user_id, preorder=preorder, state=True)
    cb_data_false = OrderRespondConfirmCallback(order_id=order_id, user_id=user_id, preorder=preorder, state=False)
    b_true = InlineKeyboardButton(text="Approve", callback_data=cb_data_true.pack())
    b_false = InlineKeyboardButton(text="Decline", callback_data=cb_data_false.pack())
    blr.add(b_true, b_false)
    return blr.as_markup()


async def create_response(
    user_db: models.UserDB,
    order_id: int,
    data: schemas.OrderResponseExtra,
    pre: bool = False,
) -> tuple[int, schemas.OrderResponse | None]:
    resp = await api_service.request(
        f"response?order_id={order_id}&is_preorder={pre}",
        "POST",
        user_db.get_token(),
        json=data.model_dump(),
    )
    if resp.status_code == 201:
        return resp.status_code, schemas.OrderResponse.model_validate(resp.json())
    return resp.status_code, None


async def update_response(
    session: AsyncSession,
    user_db: models.UserDB,
    approve: bool,
    order_id: int,
    booster_id: int,
    preorder: bool,
) -> int:
    resp = await api_service.request(
        f"response/{order_id}/{booster_id}?approve={approve}&is_preorder={preorder}",
        "PATCH",
        user_db.get_token(),
    )
    if resp.status_code in (404, 400, 403, 409):
        return resp.status_code
    for msg in await message_service.get_by_order_id_type(session, order_id, models.MessageType.RESPONSE):
        if msg.user_id == booster_id:
            text = await render_flows.get_order_text(
                user_db,
                order_id,
                with_response=True,
                response_checked=True,
                response_user_id=booster_id,
            )
            _, status = await message_service.update(session, msg, models.MessageUpdate(text=text))
        else:
            await message_service.delete(session, msg)
    return 200


async def send_response(session: AsyncSession, channel_id: int, text: str) -> models.SuccessCallback:
    msg, status = await message_service.create(
        session,
        models.MessageCreate(channel_id=channel_id, text=text, type=models.MessageType.MESSAGE),
    )
    return models.SuccessCallback(status=status, channel_id=channel_id, message_id=msg.message_id)


async def response_approved(
    session: AsyncSession,
    order: schemas.OrderRead,
    user_id: int,
    response: schemas.OrderResponse,
    text: str,
) -> models.SuccessCallback:
    user_db = await api_service.get_by_user_id(session, user_id)
    data = {"order": order, "resp": response}
    order_text = render_flows.user("response_approved", user_db, data=data)
    order_text = order_text.format(rendered_order=text)
    return await send_response(session, user_db.telegram_user_id, order_text)


async def response_declined(
    session: AsyncSession,
    user_id: int,
    order_id: int,
) -> models.SuccessCallback:
    user_db = await api_service.get_by_user_id(session, user_id)
    text = render_flows.user("response_declined", user_db, data={"order_id": order_id})
    return await send_response(session, user_db.telegram_user_id, text)


async def response_to_admins(
    session: AsyncSession,
    order: schemas.Order,
    preorder: schemas.PreOrder,
    user: schemas.User,
    text: str,
    is_preorder: bool,
) -> models.SuccessCallback:
    order_rv = order if not is_preorder else preorder

    message = await message_service.get_by_order_id_user_id(session, order_rv.id, user.id)
    if message:
        await message_service.delete(session, message)

    msg, status = await message_service.create(
        session,
        models.MessageCreate(
            order_id=order_rv.id if not is_preorder else preorder.id,
            user_id=user.id,
            channel_id=config.app.admin_order,
            text=text,
            reply_markup=get_reply_markup_admin(order_rv.id if not is_preorder else preorder.id, user.id, is_preorder),
            type=models.MessageType.RESPONSE,
        ),
    )

    return models.SuccessCallback(status=status, channel_id=msg.channel_id, message_id=msg.message_id)
