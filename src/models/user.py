import enum
import functools
from datetime import datetime, timedelta

import pytz
from pydantic import BaseModel
from sqlalchemy import BigInteger, DateTime, Enum, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.core import db

from src.schemas import User, UserLanguage, UserWithPayrolls


__all__ = (
    "OrderSelection",
    "UserDB",
    "UserCreate",
    "UserUpdate",
)


class OrderSelection(enum.Enum):
    InProgress = "In Progress"
    Completed = "Completed"
    ALL = "ALL"


class UserDB(db.TimeStampMixin):
    __tablename__ = "user"
    user_id: Mapped[int] = mapped_column(BigInteger(), nullable=False)
    telegram_user_id: Mapped[int] = mapped_column(BigInteger(), nullable=False, unique=True)
    token: Mapped[str | None] = mapped_column(Text(), nullable=True)
    user_json: Mapped[dict | None] = mapped_column(JSONB(), nullable=True)

    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    language: Mapped[UserLanguage] = mapped_column(Enum(UserLanguage), nullable=True, default=UserLanguage.EN)

    @functools.cached_property
    def user(self) -> UserWithPayrolls | None:
        if self.user_json is None:
            return None
        return UserWithPayrolls.model_validate(self.user_json)

    def get_token(self):
        if self.last_login is None or self.last_login < (datetime.now() - timedelta(days=1)).astimezone(pytz.UTC):
            return None
        return self.token


class UserCreate(BaseModel):
    user_id: int
    telegram_user_id: int


class UserUpdate(BaseModel):
    token: str | None = None
    user_json: User | None = None
    language: UserLanguage | None = None
    last_login: datetime | None = None
