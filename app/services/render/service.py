from beanie import PydanticObjectId

from . import models


async def get(config: PydanticObjectId) -> models.RenderConfig:
    return await models.RenderConfig.find_one({"_id": config})


async def create(config_in: models.RenderConfigCreate) -> models.RenderConfig:
    config = models.RenderConfig(**config_in.model_dump())
    return await config.create()


async def delete(config_id: PydanticObjectId):
    config = await models.RenderConfig.get(config_id)
    await config.delete()


async def get_by_name(name: str) -> models.RenderConfig:
    return await models.RenderConfig.find_one({"name": name})


async def get_by_names(names: list[str]) -> list[models.RenderConfig]:
    return await models.RenderConfig.find({"name": {"$in": names}}).to_list()


async def get_all() -> list[models.RenderConfig]:
    return await models.RenderConfig.find({}).to_list()


async def update(config: models.RenderConfig, config_in: models.RenderConfigUpdate):
    config_data = config.model_dump()
    update_data = config_in.model_dump(exclude_none=True)

    for field in config_data:
        if field in update_data:
            setattr(config, field, update_data[field])

    await config.save_changes()
    return config
