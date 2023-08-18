from app.services.api import schemas as api_schemas
from app.services.response import models as response_models

from . import models, service


def get_base_names(order: api_schemas.Order):
    return ["base", order.info.game, "eta-price"]


def get_base_respond_names(order: api_schemas.Order):
    return ["base", order.info.game, "eta-price", "resp"]


async def get_by_base_name(order: api_schemas.Order):
    return await service.get_by_names(get_base_names(order))


async def get_by_base_respond_names(order: api_schemas.Order):
    return await service.get_by_names(get_base_respond_names(order))


def render_order(
        order: api_schemas.Order,
        configs: list[models.RenderConfig], *,
        response: response_models.OrderResponseAPI = None
):
    out: list[str] = []
    data = {"order": order.model_dump()}
    if response:
        data["response"] = response.model_dump()
    for i, config in enumerate(configs, 1):
        config_d = []
        for index, cf in enumerate(config.fields, 0):
            attrs = []
            for fof in cf.fields:
                d = data.copy()
                for st in fof.storage:
                    d = d[st]
                attr = d.get(fof.attr)
                if attr is not None:
                    if fof.format:
                        attr = f"{attr:{fof.format}}"
                    if fof.before_value:
                        attr = f"{fof.before_value}{attr}"
                    if fof.after_value:
                        attr = f"{attr}{fof.after_value}"
                    if not isinstance(attr, str):
                        attr = str(attr)
                    attrs.append(attr)

            if attrs:
                name = cf.name
                value = cf.separator.join(attrs)

                if cf.markdown_name:
                    name = f"{cf.markdown_name}{name}:</{cf.markdown_name[1:]}"
                if cf.markdown_value:
                    value = f"{cf.markdown_value}{value}</{cf.markdown_value[1:]}"

                if len(config_d) != 0:
                    rendered = f"{config.separator_field}{name} {value}"
                else:
                    rendered = f"{name} {value}"
                config_d.append(rendered)

        out.append("".join(config_d))

        if i < len(configs) and config_d:
            out.append(config.separator)

    return "".join(out)
