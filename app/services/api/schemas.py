import datetime
import enum

from pydantic import BaseModel, EmailStr, model_validator
from pydantic_extra_types.payment import PaymentCardNumber
from pydantic_extra_types.phone_numbers import PhoneNumber

__all__ = ("User", "UserLanguage")


class UserLanguage(str, enum.Enum):
    RU = "ru"
    EN = "en"


class User(BaseModel):
    id: str
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool

    name: str
    telegram: str
    phone: PhoneNumber | None
    bank: str | None
    bankcard: PaymentCardNumber | None
    binance_email: EmailStr | None
    binance_id: int | None
    discord: str | None

    language: UserLanguage
    max_orders: int
    created_at: datetime.datetime


class OrderInfo(BaseModel):
    boost_type: str
    region_fraction: str | None
    server: str | None
    category: str | None
    character_class: str | None
    platform: str | None
    game: str
    purchase: str | None
    comment: str | None
    eta: str | None


class OrderPrice(BaseModel):
    price_booster_dollar: float | None = None
    price_booster_rub: float | None = None
    price_booster_gold: float | None = None


class OrderCredentials(BaseModel):
    battle_tag: str | None
    nickname: str | None
    login: str | None
    password: str | None
    vpn: str | None
    discord: str | None


class Order(BaseModel):
    id: str
    order_id: str

    info: OrderInfo
    price: OrderPrice


class OrderRead(Order):
    id: str
    order_id: str
    screenshot: str | None
    status: str

    info: OrderInfo
    price: OrderPrice
    credentials: OrderCredentials

    paid_time: datetime.datetime | None
    auth_date: datetime.datetime | None
    end_date: datetime.datetime | None


class PreOrder(BaseModel):
    id: str

    info: OrderInfo
    price: OrderPrice


class UserUpdate(BaseModel):
    phone: PhoneNumber | None = None
    bank: str | None = None
    bankcard: PaymentCardNumber | None = None
    binance_email: EmailStr | None = None
    binance_id: int | None = None
    max_orders: int

    @model_validator(mode="after")
    def check_passwords_match(self) -> "UserUpdate":
        if self.phone and not self.bank:
            raise ValueError("When filling in the phone number, you must also fill in the name of the bank")

        return self
