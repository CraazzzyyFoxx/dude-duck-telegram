import enum

from pydantic import BaseModel, Field, HttpUrl

from app.services.api import schemas as api_schemas
from app.services.message import models as message_models
from app.services.response import models as response_models


class MessageEnum(int, enum.Enum):
    SEND_ORDER = 0
    EDIT_ORDER = 1
    DELETE_ORDER = 2

    RESPONSE_ORDER_ADMINS = 3
    RESPONSE_ORDER_APPROVED = 4
    RESPONSE_ORDER_DECLINED = 5

    LOGGED = 6
    REGISTERED = 7
    REQUEST_VERIFY = 8
    VERIFIED = 9

    REQUEST_CLOSE_ORDER = 10

    SENT_ORDER = 11
    EDITED_ORDER = 12
    DELETED_ORDER = 13

    RESPONSE_CHOSE = 14

    ORDER_PAID = 15

    SEND_PREORDER = 16
    EDIT_PREORDER = 17
    DELETE_PREORDER = 18

    RESPONSE_PREORDER_ADMINS = 21
    RESPONSE_PREORDER_APPROVED = 22
    RESPONSE_PREORDER_DECLINED = 23


class SuccessPull(BaseModel):
    channel_id: int
    message_id: int
    status: message_models.MessageStatus


class SkippedPull(BaseModel):
    channel_id: int
    status: message_models.MessageStatus


class OrderResponse(BaseModel):
    created: list[SuccessPull] = Field(default=[])
    updated: list[SuccessPull] = Field(default=[])
    deleted: list[SuccessPull] = Field(default=[])
    skipped: list[SkippedPull] = Field(default=[])

    error: bool = Field(default=False)
    error_msg: str | None = Field(default=None)


class MessageResponse(BaseModel):
    status: message_models.MessageStatus
    channel_id: int


class MessageEventPayload(BaseModel):
    order_id: str | None = Field(default=None)

    order: api_schemas.Order | None = Field(default=None)
    preorder: api_schemas.PreOrder | None = Field(default=None)
    pull_payload: OrderResponse | None = Field(default=None)

    categories: list[str] | None = Field(default=None)
    configs: list[str] | None = Field(default=None)

    is_preorder: bool | None = Field(default=None)

    user: api_schemas.User | None = Field(default=None)
    token: str | None = Field(default=None)

    response: response_models.OrderResponse | None = Field(default=None)
    responses: int | None = Field(default=None)

    url: HttpUrl | None = Field(default=None)
    message: str | None = Field(default=None)


class MessageEvent(BaseModel):
    type: MessageEnum
    payload: MessageEventPayload
