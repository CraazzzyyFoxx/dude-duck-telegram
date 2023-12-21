from datetime import datetime, timedelta

from pydantic import BaseModel


__all__ = (
    "OrderResponseExtra",
    "OrderResponse",
)

class OrderResponseExtra(BaseModel):
    text: str | None = None
    price: float | None = None
    start_date: datetime | None = None
    eta: timedelta | None = None


class OrderResponse(BaseModel):
    order_id: int
    user_id: int

    approved: bool
    closed: bool
    text: str | None = None
    price: float | None = None
    start_date: datetime | None = None
