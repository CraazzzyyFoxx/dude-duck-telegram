import typing

from pydantic import BaseModel, HttpUrl, StringConstraints

__all__ = ("CloseOrderForm",)


class CloseOrderForm(BaseModel):
    order_id: int
    url: HttpUrl
    message: typing.Annotated[str, StringConstraints(min_length=5, max_length=256)]
