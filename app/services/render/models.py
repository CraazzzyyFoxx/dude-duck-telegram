from pydantic import BaseModel, Field
from tortoise import fields
from tortoise.models import Model


class RenderConfig(Model):
    id: int = fields.IntField(pk=True)
    name: str = fields.TextField()
    lang: str = fields.TextField()
    binary: str = fields.TextField()
    allow_separator_top: bool = fields.BooleanField()
    separator: str = fields.TextField()

    class Meta:
        unique_together = ("name", "lang")


class RenderConfigCreate(BaseModel):
    name: str
    lang: str = Field(default="en")
    binary: str
    allow_separator_top: bool = Field(default=True)
    separator: str = Field(default="▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬")


class RenderConfigUpdate(BaseModel):
    binary: str | None = None
    allow_separator_top: bool | None = None
    separator: str | None = None


class RenderConfigRead(BaseModel):
    id: int
    name: str
    lang: str
    binary: str
    allow_separator_top: bool
    separator: str
