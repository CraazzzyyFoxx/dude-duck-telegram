import enum

from pydantic import BaseModel, Field, HttpUrl

from app.services.api import schemas as api_schemas
from app.services.response import models as response_models


class MessageEnum(int, enum.Enum):
    SEND_ORDER = 0
    EDIT_ORDER = 1
    DELETE_ORDER = 2

    RESPONSE_ADMINS = 3
    RESPONSE_APPROVED = 4
    RESPONSE_DECLINED = 5

    REQUEST_VERIFY = 6
    VERIFIED = 7

    REQUEST_CLOSE_ORDER = 8

    LOGGED = 9
    REGISTERED = 10

    SENT_ORDER = 11
    EDITED_ORDER = 12
    DELETED_ORDER = 13

    RESPONSE_CHOSE = 14


class MessageEventPayload(BaseModel):
    order: api_schemas.Order | None = Field(default=None)
    categories: list[str] | None = Field(default=None)
    configs: list[str] | None = Field(default=None)
    user: api_schemas.User | None = Field(default=None)
    response: response_models.OrderResponseAPI | None = Field(default=None)
    token: str | None = Field(default=None)
    url: HttpUrl | None = Field(default=None)
    message: str | None = Field(default=None)


class MessageEvent(BaseModel):
    type: MessageEnum
    payload: MessageEventPayload
