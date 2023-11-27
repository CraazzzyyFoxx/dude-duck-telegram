import datetime
import enum
import typing

from pydantic import BaseModel, EmailStr, model_validator, HttpUrl
from pydantic_extra_types.payment import PaymentCardNumber
from pydantic_extra_types.phone_numbers import PhoneNumber


class UserLanguage(str, enum.Enum):
    RU = "ru"
    EN = "en"


class PayrollType(str, enum.Enum):
    binance_email = "Binance Email"
    binance_id = "Binance ID"
    trc20 = "TRC 20"
    phone = "Phone"
    card = "Card"


class Payroll(BaseModel):
    user_id: int
    bank: str
    type: PayrollType | typing.Literal["Хуй знает"]
    value: str


class User(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_superuser: bool
    is_verified: bool

    name: str
    telegram: str
    discord: str | None

    language: UserLanguage
    max_orders: int
    created_at: datetime.datetime


class UserWithPayrolls(User):
    payrolls: list[Payroll]


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
    booster_dollar: float | None = None
    booster_rub: float | None = None
    booster_gold: float | None = None


class OrderCredentials(BaseModel):
    battle_tag: str | None
    nickname: str | None
    login: str | None
    password: str | None
    vpn: str | None
    discord: str | None


class Order(BaseModel):
    id: int
    order_id: str

    info: OrderInfo
    price: OrderPrice


class ScreenshotRead(BaseModel):
    id: int
    created_at: datetime.datetime

    source: str
    url: HttpUrl
    order_id: int


class OrderRead(Order):
    id: int
    order_id: str
    screenshots: list[ScreenshotRead]
    status: str

    info: OrderInfo
    price: OrderPrice
    credentials: OrderCredentials

    auth_date: datetime.datetime | None
    end_date: datetime.datetime | None


class PreOrder(BaseModel):
    id: int

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
