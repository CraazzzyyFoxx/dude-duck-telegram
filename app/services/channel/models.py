from beanie import Document, Indexed
from pydantic import BaseModel, Field


class OrderChannelBase(BaseModel):
    game: str | None = None
    category: str | None = Field(default=None, min_length=1)
    channel_id: int | None = None


class OrderChannel(Document, OrderChannelBase):
    game: Indexed(str)
    category: str | None = Field(default=None, min_length=1)
    channel_id: int


class OrderChannelCreate(OrderChannelBase):
    game: str
    channel_id: int


class OrderChannelUpdate(OrderChannelBase):
    game: str
