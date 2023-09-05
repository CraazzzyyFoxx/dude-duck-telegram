from datetime import datetime
from enum import Enum

from beanie import Document, PydanticObjectId
from pymongo import IndexModel
from pydantic import BaseModel, Field


from .schemas import User


class OrderSelection(Enum):
    InProgress = "In Progress"
    Completed = "Completed"
    ALL = "ALL"


class TelegramUser(Document):
    user_id: PydanticObjectId
    telegram_user_id: int
    token: str | None = None
    user: User | None = None

    last_login: datetime | None = None
    last_update: datetime | None = None

    class Settings:
        use_state_management = True
        state_management_save_previous = True
        indexes = [
            IndexModel(["user_id", "telegram_user_id"], unique=True),

        ]


class TelegramUserCreate(BaseModel):
    user_id: PydanticObjectId
    telegram_user_id: int


class TelegramUserUpdate(BaseModel):
    token: str | None = None
    user: User | None = None

    last_login: datetime = Field(default_factory=datetime.utcnow)
