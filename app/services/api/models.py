from datetime import datetime
from enum import Enum

from tortoise import fields
from tortoise.models import Model
from pydantic import BaseModel, Field


from .schemas import User


class OrderSelection(Enum):
    InProgress = "In Progress"
    Completed = "Completed"
    ALL = "ALL"


class TelegramUser(Model):
    user_id: str = fields.CharField(max_length=24)
    telegram_user_id: int = fields.BigIntField()
    token: str | None = fields.TextField(null=True)
    user: User | None = fields.JSONField(null=True)

    last_login: datetime | None = fields.DatetimeField()
    last_update: datetime | None = fields.DatetimeField()

    class Meta:
        unique_together = ("user_id", "telegram_user_id")


class TelegramUserCreate(BaseModel):
    user_id: str
    telegram_user_id: int


class TelegramUserUpdate(BaseModel):
    token: str | None = None
    user: User | None = None

    last_login: datetime = Field(default_factory=datetime.utcnow)
