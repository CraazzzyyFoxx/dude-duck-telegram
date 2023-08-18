import datetime
import enum

from beanie import PydanticObjectId
from pydantic import BaseModel, EmailStr
from pydantic_extra_types.payment import PaymentCardNumber
from pydantic_extra_types.phone_numbers import PhoneNumber

__all__ = ("User", "UserLanguage")


class UserLanguage(str, enum.Enum):
    RU = "ru"
    EN = "en"


class User(BaseModel):
    id: PydanticObjectId
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False

    name: str
    telegram: str
    phone: PhoneNumber | None
    bank: str | None
    bankcard: PaymentCardNumber | None
    binance: EmailStr | None
    discord: str | None

    language: UserLanguage = UserLanguage.EN
    max_orders: int
    created_at: datetime.datetime


class OrderInfo(BaseModel):
    boost_type: str | None
    region_fraction: str | None
    server: str | None
    character_class: str | None
    nickname: str | None
    game: str
    purchase: str
    comment: str | None
    eta: str | None


class OrderPrice(BaseModel):
    price_dollar: float | None = None
    price_booster_dollar: float | None = None
    price_booster_dollar_fee: float | None = None
    price_booster_rub: float | None = None
    price_booster_gold: float | None = None


class OrderCredentials(BaseModel):
    battle_tag: str | None
    login: str | None
    password: str | None
    vpn: str | None


class OrderRead(BaseModel):
    id: PydanticObjectId
    order_id: str

    date: datetime.datetime
    screenshot: str | None = None
    status: str | None = None  # TODO: оно здесь не надо

    info: OrderInfo
    credentials: OrderCredentials
    price: OrderPrice

    auth_date: datetime.datetime | None = None
    end_date: datetime.datetime | None = None

    exchange: float
    shop: str | None = None
    shop_order_id: str | int | None = None
    contact: str | None = None
    booster: str | None = None  # TODO: оно здесь не надо
    status_paid: str | None = None  # TODO: оно здесь не надо


class Order(BaseModel):
    id: PydanticObjectId
    order_id: str

    date: datetime.datetime
    exchange: float
    shop: str
    shop_order_id: str | int | None
    contact: str | None
    screenshot: str | None
    status: str
    booster: str | None
    status_paid: str

    info: OrderInfo
    price: OrderPrice
    credentials: OrderCredentials

    auth_date: datetime.datetime | None
    end_date: datetime.datetime | None
