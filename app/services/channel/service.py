from beanie import PydanticObjectId

from . import models


async def get(channel_id: PydanticObjectId) -> models.Channel | None:
    return await models.Channel.find_one({"_id": channel_id})


async def create(channel_in: models.ChannelCreate) -> models.Channel:
    channel = models.Channel.model_validate(channel_in.model_dump())
    return await channel.create()


async def update(channel: models.Channel, channel_in: models.ChannelUpdate):
    channel_data = channel.model_dump()
    update_data = channel_in.model_dump(exclude_none=True)

    for field in channel_data:
        if field in update_data:
            setattr(channel, field, update_data[field])

    await channel.save_changes()
    return channel


async def delete(channel_id: PydanticObjectId):
    channel = await models.Channel.get(channel_id)
    await channel.delete()


async def get_all() -> list[models.Channel]:
    return await models.Channel.find({}).to_list()


async def get_by_game_category(game: str, category: str = None) -> models.Channel | None:
    return await models.Channel.find_one({"game": game, "category": category})


async def get_by_game_categories(game: str, categories: list[str]) -> list[models.Channel]:
    return await models.Channel.find({"game": game, "category": {"$in": categories}}).to_list()
