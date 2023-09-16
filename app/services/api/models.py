from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field
from tortoise import fields
from tortoise.models import Model

from .schemas import User


class OrderSelection(Enum):
    InProgress = "In Progress"
    Completed = "Completed"
    ALL = "ALL"


class TelegramUser(Model):
    user_id: str = fields.CharField(max_length=24)
    telegram_user_id: int = fields.BigIntField()
    token: str | None = fields.TextField(null=True)
    user: User | None = fields.JSONField(null=True, decoder=User.model_validate_json)

    last_login: datetime | None = fields.DatetimeField(null=True)
    last_update: datetime | None = fields.DatetimeField(null=True)

    class Meta:
        unique_together = ("user_id", "telegram_user_id")


class TelegramUserCreate(BaseModel):
    user_id: str
    telegram_user_id: int


class TelegramUserUpdate(BaseModel):
    token: str | None = None
    user: User | None = None

    last_login: datetime | None = None
