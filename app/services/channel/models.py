from pydantic import BaseModel, Field
from tortoise import fields
from tortoise.models import Model


class Channel(Model):
    id: int = fields.IntField(pk=True)
    game: str = fields.TextField()
    category: str | None = fields.TextField(null=True)
    channel_id: int = fields.BigIntField()


class ChannelCreate(BaseModel):
    game: str
    category: str | None = Field(default=None, min_length=1)
    channel_id: int


class ChannelUpdate(BaseModel):
    game: str
    category: str | None = Field(default=None, min_length=1)


class ChannelRead(BaseModel):
    id: int
    game: str
    category: str | None
    channel_id: int
