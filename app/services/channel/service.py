from beanie import PydanticObjectId

from . import models


async def get(channel_id: PydanticObjectId) -> models.OrderChannel | None:
    return await models.OrderChannel.find_one({"_id": channel_id})


async def create(channel_in: models.OrderChannel) -> models.OrderChannel:
    channel = models.OrderChannel.model_validate(channel_in.model_dump())
    return await channel.create()


async def update(channel: models.OrderChannel, channel_in: models.OrderChannel):
    channel_data = channel.model_dump()
    update_data = channel_in.model_dump(exclude_none=True)

    for field in channel_data:
        if field in update_data:
            setattr(channel, field, update_data[field])

    await channel.save_changes()
    return channel


async def delete(channel_id: PydanticObjectId):
    channel = await models.OrderChannel.get(channel_id)
    await channel.delete()


async def get_all() -> list[models.OrderChannel]:
    return await models.OrderChannel.find({}).to_list()


async def get_channel_by_game_category(game: str, category: str = None) -> models.OrderChannel | None:
    return await models.OrderChannel.find_one({"game": game, "category": category})


async def get_channels_by_game_categories(game: str, categories: list[str]) -> list[models.OrderChannel]:
    return await models.OrderChannel.find({"game": game, "category": {"$in": categories}}).to_list()
