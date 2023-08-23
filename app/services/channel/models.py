from beanie import Document, Indexed, PydanticObjectId
from pydantic import BaseModel, Field


class Channel(Document, BaseModel):
    game: Indexed(str)
    category: str | None = Field(default=None, min_length=1)
    channel_id: int

    class Settings:
        use_state_management = True
        state_management_save_previous = True


class ChannelCreate(BaseModel):
    game: str
    category: str | None = Field(default=None, min_length=1)
    channel_id: int


class ChannelUpdate(BaseModel):
    game: str
    category: str | None = Field(default=None, min_length=1)


class ChannelRead(BaseModel):
    id: PydanticObjectId
    game: str
    category: str | None
    channel_id: int
