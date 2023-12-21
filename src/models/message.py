import enum
from datetime import datetime

from aiogram.types import ForceReply, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from pydantic import BaseModel, Field
from sqlalchemy import BigInteger, Enum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.core import db, enums


__all__ = (
    "MessageType",
    "CallbackStatus",
    "Message",
    "MessageCreate",
    "MessageUpdate",
    "SuccessCallback",
    "SkippedCallback",
    "MessageCallback",
    "MessageResponse",
    "OrderMessageCreate",
    "OrderMessageRead",
    "OrderMessageUpdate",
    "OrderMessageDelete",
    "UserMessageRead",
)


class MessageType(str, enum.Enum):
    ORDER = "order"
    PRE_ORDER = "pre_order"
    RESPONSE = "response"
    MESSAGE = "message"


class CallbackStatus(str, enum.Enum):
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"

    NOT_FOUND = "not_found"
    SAME_TEXT = "same_text"
    FORBIDDEN = "forbidden"
    EXISTS = "exists"


class Message(db.TimeStampMixin):
    __tablename__ = "message"
    __table_args__ = (UniqueConstraint("channel_id", "message_id", name="idx_channel_message"),)

    order_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    message_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    type: Mapped[MessageType] = mapped_column(Enum(MessageType))


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


class SuccessCallback(BaseModel):
    channel_id: int
    message_id: int
    status: CallbackStatus


class SkippedCallback(BaseModel):
    channel_id: int
    status: CallbackStatus


class MessageCallback(BaseModel):
    created: list[SuccessCallback] = Field(default=[])
    updated: list[SuccessCallback] = Field(default=[])
    deleted: list[SuccessCallback] = Field(default=[])
    skipped: list[SkippedCallback] = Field(default=[])

    error: bool = Field(default=False)
    error_msg: str | None = Field(default=None)


class MessageResponse(BaseModel):
    status: CallbackStatus
    channel_id: int


class OrderMessageCreate(BaseModel):
    channel_id: int
    order_id: int
    text: str
    is_preorder: bool


class OrderMessageRead(BaseModel):
    id: int
    channel_id: int
    message_id: int
    integration: enums.Integration
    is_deleted: bool
    created_at: datetime
    order_id: int
    is_preorder: bool


class OrderMessageUpdate(BaseModel):
    message: OrderMessageRead
    text: str


class OrderMessageDelete(BaseModel):
    message: OrderMessageRead


class UserMessageRead(BaseModel):
    id: int
    channel_id: int
    message_id: int
    integration: enums.Integration
    is_deleted: bool
    created_at: datetime
    user_id: int
