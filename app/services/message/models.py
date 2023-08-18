from datetime import datetime
from enum import Enum

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply
from beanie import PydanticObjectId, Document
from pydantic import BaseModel, Field


class MessageType(str, Enum):
    ORDER = "order"
    RESPONSE = "response"
    MESSAGE = "message"


class Message(Document, BaseModel):
    order_id: PydanticObjectId | None = None
    user_id: PydanticObjectId | None = None
    channel_id: int
    message_id: int

    type: MessageType

    is_deleted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MessageCreate(BaseModel):
    order_id: PydanticObjectId | None = None
    user_id: PydanticObjectId | None = None
    channel_id: int

    type: MessageType

    text: str
    reply_markup: InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None = Field(default=None)


class MessageUpdate(BaseModel):
    text: str
    inline_keyboard: InlineKeyboardMarkup
