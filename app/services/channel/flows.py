from fastapi import HTTPException
from starlette import status

from . import models, service


async def get(channel_id: int) -> models.Channel:
    channel = await service.get(channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A channel with this id does not exist."}],
        )
    return channel


async def get_channel_by_game_category(game: str, category: str = None) -> models.Channel:
    channel = await service.get_by_game_category(game, category)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A channel with this game and category does not exist."}],
        )
    return channel


async def create(channel_in: models.ChannelCreate) -> models.Channel:
    channel = await service.get_by_game_category(channel_in.game, channel_in.category)
    if channel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[{"msg": "A channel with this game and category already exists."}],
        )
    channel = await service.create(channel_in)
    return channel


async def delete(channel_id: int):
    channel = await get(channel_id)
    await service.delete(channel_id)
    return channel
