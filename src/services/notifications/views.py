from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from fastapi import APIRouter, Body, Depends

from src.core import config, db, enums
from src import models, schemas
from src.core.cbdata import VerifyCallback
from src.services.api import service as api_service
from src.services.api import flows as api_flows
from src.services.auth.bearers import requires_authorization
from src.services.message import service as message_service
from src.services.render import flows as render_flows
from src.services.response import flows as response_flows

router = APIRouter(
    prefix="/notification", tags=[enums.RouteTag.NOTIFICATIONS], dependencies=[Depends(requires_authorization)]
)


def get_reply_markup_verification(user_id: int) -> InlineKeyboardMarkup:
    blr = InlineKeyboardBuilder()
    cb_data_true = VerifyCallback(user_id=user_id, state=True)
    cb_data_false = VerifyCallback(user_id=user_id, state=False)
    b_true = InlineKeyboardButton(text="Approve", callback_data=cb_data_true.pack())
    b_false = InlineKeyboardButton(text="Decline", callback_data=cb_data_false.pack())
    blr.add(b_true, b_false)
    return blr.as_markup()


@router.post("/response_approved", response_model=models.MessageResponse)
async def response_approved_notification(
    user: schemas.User,
    order: schemas.OrderRead,
    response: schemas.OrderResponse,
    text: str = Body(..., embed=True),
    session=Depends(db.get_async_session),
):
    return await response_flows.response_approved(session, order, user.id, response, text)


@router.post("/response_declined", response_model=models.MessageResponse)
async def response_declined_notification(
    user_id: int,
    order_id: int = Body(..., embed=True),
    session=Depends(db.get_async_session),
):
    return await response_flows.response_declined(session, user_id, order_id)


@router.post("/logged", response_model=models.MessageResponse)
async def logged_notification(
        user: schemas.User = Body(..., embed=True),
        session=Depends(db.get_async_session)
):
    _, status = await message_service.create(
        session,
        models.MessageCreate(
            text=render_flows.system("notify_logged", data={"user": user}),
            channel_id=config.app.admin_events,
            type=models.MessageType.MESSAGE,
        ),
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_events)


@router.post("/registered", response_model=models.MessageResponse)
async def registered_notification(
        user: schemas.User = Body(..., embed=True),
        session=Depends(db.get_async_session)
):
    _, status = await message_service.create(
        session,
        models.MessageCreate(
            text=render_flows.system("notify_registered", data={"user": user}),
            channel_id=config.app.admin_important_events,
            type=models.MessageType.MESSAGE,
        ),
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_important_events)


@router.post("/request_verify", response_model=models.MessageResponse)
async def request_verify_notification(
    user: schemas.User = Body(..., embed=True),
    session=Depends(db.get_async_session),
):
    msg, status = await message_service.create(
        session,
        models.MessageCreate(
            text=render_flows.system("notify_verify", data={"user": user}),
            channel_id=config.app.admin_important_events,
            type=models.MessageType.MESSAGE,
            reply_markup=get_reply_markup_verification(user.id),
        ),
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_important_events)


@router.post("/verified", response_model=models.MessageResponse)
async def verified_notification(
        user: schemas.User = Body(..., embed=True),
        session=Depends(db.get_async_session)
):
    user_db = await api_service.get_by_user_id(session, user.id)
    user = await api_flows.get_me(session, user_db)
    if not user_db:
        return models.MessageResponse(
            status=models.CallbackStatus.NOT_FOUND, channel_id=user_db.telegram_user_id
        )
    await api_service.update(session, user_db, models.UserUpdate(user_json=user))
    _, status = await message_service.create(
        session,
        models.MessageCreate(
            text=render_flows.user("verified", user_db),
            channel_id=user_db.telegram_user_id,
            type=models.MessageType.MESSAGE,
        ),
    )
    return models.MessageResponse(status=status, channel_id=user_db.telegram_user_id)


@router.post("/order_close_request", response_model=models.MessageResponse)
async def order_close_request_notification(
    user: schemas.User,
    order_id: str = Body(..., embed=True),
    url: str = Body(..., embed=True),
    message: str = Body(..., embed=True),
    session=Depends(db.get_async_session),
):
    data = {"user": user, "order_id": order_id, "url": url, "message": message}
    _, status = await message_service.create(
        session,
        models.MessageCreate(
            text=render_flows.system("notify_order_close", data=data),
            channel_id=config.app.admin_important_events,
            type=models.MessageType.MESSAGE,
        ),
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_important_events)


@router.post("/order_sent", response_model=models.MessageResponse)
async def order_sent_notification(
    payload: models.MessageCallback,
    order_id: str = Body(..., embed=True),
    session=Depends(db.get_async_session),
):
    data = {"order_id": order_id, "payload": payload}
    _, status = await message_service.create(
        session,
        models.MessageCreate(
            text=render_flows.system("notify_order_sent", data=data),
            channel_id=config.app.admin_noise_events,
            type=models.MessageType.MESSAGE,
        ),
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_noise_events)


@router.post("/order_edited", response_model=models.MessageResponse)
async def order_edited_notification(
    payload: models.MessageCallback,
    order_id: str = Body(..., embed=True),
    session=Depends(db.get_async_session),
):
    data = {"order_id": order_id, "payload": payload}
    _, status = await message_service.create(
        session,
        models.MessageCreate(
            text=render_flows.system("notify_order_edited", data=data),
            channel_id=config.app.admin_noise_events,
            type=models.MessageType.MESSAGE,
        ),
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_noise_events)


@router.post("/order_deleted", response_model=models.MessageResponse)
async def order_deleted_notification(
    payload: models.MessageCallback,
    order_id: str = Body(..., embed=True),
    session=Depends(db.get_async_session),
):
    data = {"order_id": order_id, "payload": payload}
    _, status = await message_service.create(
        session,
        models.MessageCreate(
            text=render_flows.system("notify_order_deleted", data=data),
            channel_id=config.app.admin_noise_events,
            type=models.MessageType.MESSAGE,
        ),
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_noise_events)


@router.post("/response_chose", response_model=models.MessageResponse)
async def response_chose_notification(
    user: schemas.User = Body(..., embed=True),
    order_id: str = Body(..., embed=True),
    responses: int = Body(..., embed=True),
    session=Depends(db.get_async_session),
):
    data = {"order_id": order_id, "total": responses, "user": user}
    _, status = await message_service.create(
        session,
        models.MessageCreate(
            text=render_flows.system("notify_response_chose", data=data),
            channel_id=config.app.admin_events,
            type=models.MessageType.MESSAGE,
        ),
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_events)


@router.post("/order_paid", response_model=models.MessageResponse)
async def order_paid_notification(
    order: schemas.Order,
    user: schemas.User,
    session=Depends(db.get_async_session),
):
    _, status = await message_service.create(
        session,
        models.MessageCreate(
            text=render_flows.system("notify_order_paid", data={"order": order, "user": user}),
            channel_id=config.app.admin_events,
            type=models.MessageType.MESSAGE,
        ),
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_events)
