from fastapi import APIRouter, Body, Depends

from src.core import db, enums
from src import models, schemas
from src.services.api import service as api_service
from src.services.auth.bearers import requires_authorization
from src.services.message import service as message_service
from src.services.response import flows as response_flows

from . import flows

router = APIRouter(
    prefix="/message",
    tags=[enums.RouteTag.ORDER_MESSAGES],
    dependencies=[Depends(requires_authorization)],
)


@router.post("/order", response_model=models.MessageCallback)
async def order_create(params: models.OrderMessageCreate, session=Depends(db.get_async_session)):
    return await flows.create_order_message(session, params)


@router.patch("/order", response_model=models.MessageCallback)
async def order_update(params: models.OrderMessageUpdate, session=Depends(db.get_async_session)):
    return await flows.update_order_message(session, params)


@router.delete("/order", response_model=models.MessageCallback)
async def order_delete(params: models.OrderMessageDelete, session=Depends(db.get_async_session)):
    return await flows.delete_order_message(session, params)


@router.post("/response_admins", response_model=models.MessageCallback)
async def order_admins_notify(
    user: schemas.User,
    is_preorder: bool = Body(..., embed=True),
    text: str = Body(..., embed=True),
    order: schemas.Order | None = None,
    preorder: schemas.PreOrder | None = None,
    session=Depends(db.get_async_session),
):
    resp = await response_flows.response_to_admins(session, order, preorder, user, text, is_preorder)
    return models.MessageCallback(created=[resp])


@router.post("/user", response_model=models.MessageCallback)
async def create_user_message(
    user_id: int = Body(..., embed=True),
    text: str = Body(..., embed=True),
    session=Depends(db.get_async_session),
):
    user_db = await api_service.get_by_user_id(session, user_id)
    if not user_db:
        return models.MessageResponse(
            status=models.CallbackStatus.NOT_FOUND, channel_id=user_db.telegram_user_id
        )
    msg, status = await message_service.create(
        session,
        models.MessageCreate(
            text=text,
            channel_id=user_db.telegram_user_id,
            type=models.MessageType.MESSAGE,
        ),
    )
    created, skipped = [], []
    if msg:
        created = [models.SuccessCallback(status=status, channel_id=msg.channel_id, message_id=msg.message_id)]
    else:
        skipped = [models.SkippedCallback(status=status, channel_id=user_db.telegram_user_id)]
    return models.MessageCallback(created=created, skipped=skipped)


@router.patch("/user", response_model=models.MessageCallback)
async def update_user_message(
    message: models.UserMessageRead,
    text: str = Body(..., embed=True),
    session=Depends(db.get_async_session),
):
    message_db = await message_service.get_by_channel_id_message_id(session, message.channel_id, message.message_id)
    msg, status = await message_service.update(
        session, message_db, models.MessageUpdate(text=text)
    )
    updated, skipped = [], []
    if msg:
        updated = [models.SuccessCallback(status=status, channel_id=msg.channel_id, message_id=msg.message_id)]
    else:
        skipped = [models.SkippedCallback(status=status, channel_id=message.channel_id)]
    return models.MessageCallback(updated=updated, skipped=skipped)


@router.delete("/user", response_model=models.MessageCallback)
async def delete_user_message(
    message: models.UserMessageRead = Body(..., embed=True),
    session=Depends(db.get_async_session),
):
    message_db = await message_service.get_by_channel_id_message_id(session, message.channel_id, message.message_id)
    msg, status = await message_service.delete(session, message_db)
    deleted, skipped = [], []
    if msg:
        deleted = [models.SuccessCallback(status=status, channel_id=msg.channel_id, message_id=msg.message_id)]
    else:
        skipped = [models.SkippedCallback(status=status, channel_id=message.channel_id)]
    return models.MessageCallback(deleted=deleted, skipped=skipped)
