from beanie import PydanticObjectId

from . import models


async def get(response_id: PydanticObjectId) -> models.OrderResponse | None:
    return await models.OrderResponse.find_one({"_id": response_id})


async def create(response_in: models.OrderResponseCreate):
    response = models.OrderResponse(**response_in.model_dump())
    return await response.create()


async def delete(response_id: PydanticObjectId):
    user_order = await models.OrderResponse.get(response_id)
    await user_order.delete()


async def get_by_order_id(order_id: PydanticObjectId) -> list[models.OrderResponse]:
    return await models.OrderResponse.find({"order_id": order_id}).to_list()


async def get_by_order_id_user_id(order_id: PydanticObjectId, user_id: PydanticObjectId) -> models.OrderResponse | None:
    return await models.OrderResponse.find_one({"order_id": order_id}, {"user_id": user_id})


async def get_all() -> list[models.OrderResponse]:
    return await models.OrderResponse.find({}).to_list()
