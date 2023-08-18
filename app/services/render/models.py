from pydantic import BaseModel, Field, field_validator
from beanie import Document, Indexed

__all__ = (
    "RenderConfig",
    "RenderFieldConfig",
    "RenderField",
    "RenderConfigCreate",
    "RenderConfigUpdate",
)


class RenderField(BaseModel):
    attr: str = Field(strict=True)
    storage: list[str]
    format: str | None = Field(default=None, strict=True)
    before_value: str | None = Field(default=None, min_length=1, max_length=20, strict=True)
    after_value: str | None = Field(default=None, min_length=1, max_length=20, strict=True)


class RenderFieldConfig(BaseModel):
    name: str = Field(strict=True)
    fields: list[RenderField]
    markdown_name: str | None = Field(default=None, strict=True, min_length=3, max_length=6)
    markdown_value: str | None = Field(default=None, strict=True, min_length=3, max_length=6)
    separator: str = Field(default=' ', min_length=1, max_length=20, strict=True)

    @field_validator('markdown_name', 'markdown_value')
    def parse_markdown(cls, v: str):
        if v is None:
            return v
        if not v.startswith('<'):
            raise ValueError(f"Invalid markdown element. Example: <code>")
        if not v.endswith('>'):
            raise ValueError(f"Invalid markdown element. Example: <code>")
        if v[1:-1] not in ["b", "i", "code", "s", "u", "pre"]:
            raise ValueError(f"Invalid markdown element. It's can be [b|i|code|s|u|pre]")
        return v


class RenderConfig(Document):
    name: Indexed(str, unique=True) = Field(min_length=1, max_length=20)
    fields: list[RenderFieldConfig]
    separator: str = Field(default='\n', min_length=1, max_length=24)
    separator_field: str = Field(default='\n', min_length=1, max_length=24)

class RenderConfigCreate(RenderConfig):
    pass


class RenderConfigUpdate(RenderConfig):
    name: str = Field(min_length=1, max_length=20, strict=True)
    fields: list[RenderFieldConfig]
    separator: str | None = Field(default=None, min_length=1, max_length=20, strict=True)
    separator_field: str | None = Field(default=None, min_length=1, max_length=20, strict=True)
