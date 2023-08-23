from datetime import datetime
from enum import Enum

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply
from beanie import PydanticObjectId, Document
from pydantic import BaseModel, Field
from pymongo import IndexModel


class MessageType(str, Enum):
    ORDER = "order"
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


class Message(Document, BaseModel):
    order_id: PydanticObjectId | None = None
    user_id: PydanticObjectId | None = None
    channel_id: int
    message_id: int

    type: MessageType

    is_deleted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        indexes = [
            IndexModel(["channel_id", "message_id"], unique=True),
            # IndexModel(["order_id", "channel_id", "type"], unique=True),
        ]
        use_state_management = True
        state_management_save_previous = True


class MessageRead(BaseModel):
    order_id: PydanticObjectId | None = None
    user_id: PydanticObjectId | None = None
    channel_id: int
    message_id: int

    type: MessageType

    is_deleted: bool
    created_at: datetime


class MessageCreate(BaseModel):
    order_id: PydanticObjectId | None = None
    user_id: PydanticObjectId | None = None
    channel_id: int

    type: MessageType

    text: str
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = Field(default=None)


class MessageUpdate(BaseModel):
    text: str | None = None
    inline_keyboard: InlineKeyboardMarkup | None = None
