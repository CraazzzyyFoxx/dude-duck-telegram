from datetime import timedelta, datetime

from pydantic import BaseModel, Field
from beanie import Document, PydanticObjectId

__all__ = (
    "OrderResponse",
    "OrderResponseExtra",
    "OrderResponseCreate"
)


class OrderResponseExtra(BaseModel):
    text: str | None = None
    price: float | None = None
    start_date: datetime | None = None
    eta: timedelta | None = None


class OrderResponseCreate(BaseModel):
    order_id: PydanticObjectId
    user_id: PydanticObjectId
    channel_id: int
    message_id: int


class OrderResponse(BaseModel):
    order_id: PydanticObjectId
    user_id: PydanticObjectId

    approved: bool = Field(default=False)
    closed: bool = Field(default=False)
    extra: OrderResponseExtra
