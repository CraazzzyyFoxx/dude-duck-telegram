from fastapi import APIRouter, Body, Depends

from src.core import config, enums
from src.services.api import models as api_models
from src.services.api import schemas as api_schemas
from src.services.api import service as api_service
from src.services.auth.bearers import requires_authorization
from src.services.message import models as message_models
from src.services.message import service as message_service
from src.services.render import flows as render_flows
from src.services.response import flows as response_flows

from . import flows, models

router = APIRouter(
    prefix="/message", tags=[enums.RouteTag.ORDER_MESSAGES], dependencies=[Depends(requires_authorization)]
)


@router.post("/order_create", response_model=models.OrderResponse)
async def order_create(params: models.PullCreate):
    return await flows.pull_create(params)


@router.post("/order_update", response_model=models.OrderResponse)
async def order_update(params: models.PullUpdate):
    return await flows.pull_update(params)


@router.post("/order_delete", response_model=models.OrderResponse)
async def order_delete(params: models.PullDelete):
    return await flows.pull_delete(params)


@router.post("/order_admins", response_model=models.MessageResponse)
async def order_admins_notify(
    user: api_schemas.User,
    is_preorder: bool = Body(..., embed=True),
    text: str = Body(..., embed=True),
    order: api_schemas.Order | None = None,
    preorder: api_schemas.PreOrder | None = None,
):
    return await response_flows.response_to_admins(order, preorder, user, text, is_preorder)


@router.post("/user_resp_approved_notify", response_model=list[models.MessageResponse])
async def user_resp_approved_notify(
    user: api_schemas.User,
    order: api_schemas.OrderRead,
    response: response_flows.models.OrderResponse,
    text: str = Body(..., embed=True),
):
    return await response_flows.response_approved(order, user, response, text)


@router.post("/user_resp_declined_notify", response_model=list[models.MessageResponse])
async def user_resp_declined_notify(
    user: api_schemas.User,
    order_id: int = Body(..., embed=True),
):
    return await response_flows.response_declined(user, order_id)


@router.post("/logged_notify", response_model=models.MessageResponse)
async def logged_notify(user: api_schemas.User):
    data = {"user": user}
    _, status = await message_service.create(
        message_models.MessageCreate(
            text=render_flows.system("notify_logged", data=data),
            channel_id=config.app.admin_events,
            type=message_models.MessageType.MESSAGE,
        )
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_events)


@router.post("/registered_notify", response_model=models.MessageResponse)
async def registered_notify(user: api_schemas.User):
    data = {"user": user}
    _, status = await message_service.create(
        message_models.MessageCreate(
            text=render_flows.system("notify_registered", data=data),
            channel_id=config.app.admin_important_events,
            type=message_models.MessageType.MESSAGE,
        )
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_important_events)


@router.post("/request_verify_notify", response_model=models.MessageResponse)
async def request_verify_notify(user: api_schemas.User, token: str = Body(..., embed=True)):
    data = {"user": user, "token": token}
    _, status = await message_service.create(
        message_models.MessageCreate(
            text=render_flows.system("notify_verify", data=data),
            channel_id=config.app.admin_important_events,
            type=message_models.MessageType.MESSAGE,
        )
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_important_events)


@router.post("/verified_notify", response_model=list[models.MessageResponse])
async def verified_notify(user: api_schemas.User):
    resp = []

    users_db = await api_service.get_by_user_id(user.id)
    for user_db in users_db:
        await api_service.update(user_db, api_models.TelegramUserUpdate(user=user, token=user_db.token))
        _, status = await message_service.create(
            message_models.MessageCreate(
                text=render_flows.user("verified", user),
                channel_id=user_db.telegram_user_id,
                type=message_models.MessageType.MESSAGE,
            )
        )
        resp.append(models.MessageResponse(status=status, channel_id=config.app.admin_important_events))
    return resp


@router.post("/order_close_request_notify", response_model=models.MessageResponse)
async def order_close_request_notify(
    user: api_schemas.User,
    order_id: str = Body(..., embed=True),
    url: str = Body(..., embed=True),
    message: str = Body(..., embed=True),
):
    data = {"user": user, "order_id": order_id, "url": url, "message": message}
    _, status = await message_service.create(
        message_models.MessageCreate(
            text=render_flows.system("notify_order_close", data=data),
            channel_id=config.app.admin_important_events,
            type=message_models.MessageType.MESSAGE,
        )
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_important_events)


@router.post("/order_sent_notify", response_model=models.MessageResponse)
async def order_sent_notify(pull_payload: models.OrderResponse, order_id: str = Body(..., embed=True)):
    data = {"order_id": order_id, "payload": pull_payload}
    _, status = await message_service.create(
        message_models.MessageCreate(
            text=render_flows.system("notify_order_sent", data=data),
            channel_id=config.app.admin_noise_events,
            type=message_models.MessageType.MESSAGE,
        )
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_noise_events)


@router.post("/order_edited_notify", response_model=models.MessageResponse)
async def order_edited_notify(pull_payload: models.OrderResponse, order_id: str = Body(..., embed=True)):
    data = {"order_id": order_id, "payload": pull_payload}
    _, status = await message_service.create(
        message_models.MessageCreate(
            text=render_flows.system("notify_order_edited", data=data),
            channel_id=config.app.admin_noise_events,
            type=message_models.MessageType.MESSAGE,
        )
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_noise_events)


@router.post("/order_deleted_notify", response_model=models.MessageResponse)
async def order_deleted_notify(pull_payload: models.OrderResponse, order_id: str = Body(..., embed=True)):
    data = {"order_id": order_id, "payload": pull_payload}
    _, status = await message_service.create(
        message_models.MessageCreate(
            text=render_flows.system("notify_order_deleted", data=data),
            channel_id=config.app.admin_noise_events,
            type=message_models.MessageType.MESSAGE,
        )
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_noise_events)


@router.post("/response_chose_notify", response_model=models.MessageResponse)
async def response_chose_notify(
    user: api_schemas.User, order_id: str = Body(..., embed=True), responses: int = Body(..., embed=True)
):
    data = {"order_id": order_id, "total": responses, "user": user}
    _, status = await message_service.create(
        message_models.MessageCreate(
            text=render_flows.system("notify_response_chose", data=data),
            channel_id=config.app.admin_events,
            type=message_models.MessageType.MESSAGE,
        )
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_events)


@router.post("/order_paid_notify", response_model=models.MessageResponse)
async def order_paid_notify(order: api_schemas.Order, user: api_schemas.User):
    data = {"order": order, "user": user}
    _, status = await message_service.create(
        message_models.MessageCreate(
            text=render_flows.system("notify_order_paid", data=data),
            channel_id=config.app.admin_events,
            type=message_models.MessageType.MESSAGE,
        )
    )
    return models.MessageResponse(status=status, channel_id=config.app.admin_events)
