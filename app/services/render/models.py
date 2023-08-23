from pydantic import BaseModel, Field
from beanie import Document, PydanticObjectId
from pymongo import IndexModel


class RenderConfig(Document):
    name: str
    lang: str
    binary: str
    allow_separator_top: bool
    separator: str

    class Settings:
        indexes = [
            IndexModel(["name", "lang"], unique=True),
        ]
        use_state_management = True
        state_management_save_previous = True


class RenderConfigCreate(BaseModel):
    name: str
    lang: str = Field(default="en")
    binary: str
    allow_separator_top: bool = Field(default=True)
    separator: str = Field(default="▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬")


class RenderConfigUpdate(BaseModel):
    binary: str
    allow_separator_top: bool
    separator: str


class RenderConfigRead(BaseModel):
    id: PydanticObjectId
    name: str
    lang: str
    binary: str
    allow_separator_top: bool
    separator: str
