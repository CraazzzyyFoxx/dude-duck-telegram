from tortoise.expressions import Q

from app.services.api import schemas as api_schemas

from . import models


def get_all_config_names(order: api_schemas.Order | api_schemas.PreOrder) -> list[str]:
    return [
        "order",
        "eta-price",
        "eta-price-gold",
        "response",
        "response-check",
        order.info.game,
        f"{order.info.game}-cd",
        "pre-order",
        "pre-eta-price",
        "pre-eta-price-gold",
    ]


async def get(config_id: int) -> models.RenderConfig | None:
    return await models.RenderConfig.get(id=config_id)


async def create(config_in: models.RenderConfigCreate) -> models.RenderConfig:
    return await models.RenderConfig.create(**config_in.model_dump())


async def delete(config_id: int) -> None:
    config = await get(config_id)
    if config:
        await config.delete()


async def get_by_name(name: str) -> models.RenderConfig | None:
    return await models.RenderConfig.filter(name=name).first()


async def get_by_names(names: list[str]) -> list[models.RenderConfig]:
    return await models.RenderConfig.filter(Q(name__in=names)).all()


async def update(parser: models.RenderConfig, parser_in: models.RenderConfigUpdate) -> models.RenderConfig:
    update_data = parser_in.model_dump(exclude_none=True)
    parser = parser.update_from_dict(update_data)

    await parser.save()
    return parser


async def get_all_configs_for_order(order: api_schemas.Order | api_schemas.PreOrder) -> list[models.RenderConfig]:
    return await models.RenderConfig.filter(Q(name__in=get_all_config_names(order))).all()
