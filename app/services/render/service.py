from beanie import PydanticObjectId

from app.services.api.schemas import Order

from . import models


def get_all_config_names(order: Order):
    return ["order", "eta-price", "response", "response-check",
            order.info.game, f"{order.info.game}-cd", "pre-order", "pre-eta-price"]

async def get(config_id: PydanticObjectId) -> models.RenderConfig | None:
    return await models.RenderConfig.find_one({"_id": config_id})


async def create(config_in: models.RenderConfigCreate) -> models.RenderConfig:
    config = models.RenderConfig(**config_in.model_dump())
    return await config.create()


async def delete(config_id: PydanticObjectId):
    user_order = await models.RenderConfig.get(config_id)
    await user_order.delete()


async def get_by_name(name: str) -> models.RenderConfig | None:
    return await models.RenderConfig.find_one({"name": name})


async def update(parser: models.RenderConfig, parser_in: models.RenderConfigUpdate) -> models.RenderConfig:
    parser_data = parser.model_dump()
    update_data = parser_in.model_dump(exclude_none=True)

    for field in parser_data:
        if field in update_data:
            setattr(parser, field, update_data[field])

    await parser.save_changes()
    return parser


async def get_all_configs_for_order(order: Order) -> list[models.RenderConfig]:
    return await models.RenderConfig.find({"name": {"$in": get_all_config_names(order)}}).to_list()
