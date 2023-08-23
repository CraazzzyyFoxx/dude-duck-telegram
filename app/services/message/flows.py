from fastapi import HTTPException
from starlette import status
from beanie import PydanticObjectId

from . import service, models


async def get(channel: PydanticObjectId) -> models.Message:
    channel = await service.get(channel)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A channel with this id does not exist."}],
        )
    return channel


async def get_by_order_id(order_id: PydanticObjectId) -> list[models.Message]:
    messages = await service.get_by_order_id(order_id)
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A messages with this order_id does not exist."}],
        )
    return messages


async def create(message_in: models.MessageCreate) -> models.Message:
    message, st = await service.create(message_in)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[{"msg": "A message with this order_id and channel_id already exists."}],
        )
    return message
