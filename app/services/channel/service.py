from tortoise.expressions import Q

from . import models


async def get(channel_id: int) -> models.Channel | None:
    return await models.Channel.filter(id=channel_id).first()


async def create(channel_in: models.ChannelCreate) -> models.Channel:
    return await models.Channel.create(**channel_in.model_dump())


async def update(channel: models.Channel, channel_in: models.ChannelUpdate) -> models.Channel:
    update_data = channel_in.model_dump(exclude_none=True)
    channel = channel.update_from_dict(update_data)

    await channel.save()
    return channel


async def delete(channel_id: int) -> None:
    channel = await get(channel_id)
    await channel.delete()


async def get_all() -> list[models.Channel]:
    return await models.Channel.all()


async def get_by_game_category(game: str, category: str = None) -> models.Channel | None:
    return await models.Channel.filter(game=game, category=category).first()


async def get_by_game_categories(game: str, categories: list[str]) -> list[models.Channel]:
    return await models.Channel.filter(Q(game=game) & Q(category__in=categories)).all()
