from fastapi import HTTPException
from starlette import status
from beanie import PydanticObjectId

from . import service, models


async def get(channel: PydanticObjectId) -> models.OrderChannel:
    channel = await service.get(channel)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A channel with this id does not exist."}],
        )
    return channel


async def get_channel_by_game_category(game: str, category: str = None) -> models.OrderChannel:
    channel = await service.get_channel_by_game_category(game, category)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A channel with this game and category does not exist."}],
        )
    return channel


async def create(channel_in: models.OrderChannel) -> models.OrderChannel:
    channel = await service.get_channel_by_game_category(channel_in.game, channel_in.category)
    if channel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[{"msg": "A channel with this game and category already exists."}],
        )
    channel = await service.create(channel_in)
    return channel
