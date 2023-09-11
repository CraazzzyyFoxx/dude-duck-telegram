from beanie import PydanticObjectId
from pydantic import BaseModel, HttpUrl, constr


__all__ = ("CloseOrderForm", )


class CloseOrderForm(BaseModel):
    order_id: PydanticObjectId
    url: HttpUrl
    message: constr(max_length=256, min_length=5)