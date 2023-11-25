from datetime import datetime
from enum import Enum

from aiogram.types import ForceReply, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from pydantic import BaseModel, Field
from tortoise import fields
from tortoise.models import Model

from src.core import enums


class MessageType(str, Enum):
    ORDER = "order"
    PRE_ORDER = "pre_order"
    RESPONSE = "response"
    MESSAGE = "message"


class MessageStatus(str, Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"

    NOT_FOUND = "not_found"
    SAME_TEXT = "same_text"
    FORBIDDEN = "forbidden"
    EXISTS = "exists"


class Message(Model):
    id: int = fields.IntField(pk=True)
    order_id: int | None = fields.BigIntField(null=True)
    user_id: int | None = fields.BigIntField(null=True)
    channel_id: int = fields.BigIntField()
    message_id: int = fields.BigIntField()

    type: MessageType = fields.CharEnumField(MessageType)
    created_at: datetime = fields.DatetimeField(auto_now=True)

    class Meta:
        unique_together = ("channel_id", "message_id")


class MessageRead(BaseModel):
    order_id: int | None = None
    user_id: int | None = None
    channel_id: int
    message_id: int

    integration: enums.Integration
    type: MessageType

    created_at: datetime


class MessageCreate(BaseModel):
    order_id: int | None = None
    user_id: int | None = None
    channel_id: int

    type: MessageType

    text: str
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = None


class MessageUpdate(BaseModel):
    text: str | None = None
    inline_keyboard: InlineKeyboardMarkup | None = None


class SuccessPull(BaseModel):
    channel_id: int
    message_id: int
    status: MessageStatus


class SkippedPull(BaseModel):
    channel_id: int
    status: MessageStatus


class OrderResponse(BaseModel):
    created: list[SuccessPull] = Field(default=[])
    updated: list[SuccessPull] = Field(default=[])
    deleted: list[SuccessPull] = Field(default=[])
    skipped: list[SkippedPull] = Field(default=[])

    error: bool = Field(default=False)
    error_msg: str | None = Field(default=None)


class MessageResponse(BaseModel):
    status: MessageStatus
    channel_id: int


class PullCreate(BaseModel):
    channel_id: int
    order_id: int
    text: str
    is_preorder: bool


class PullUpdate(BaseModel):
    message: MessageRead
    order_id: int
    text: str
    is_preorder: bool


class PullDelete(BaseModel):
    message: MessageRead
    order_id: int
