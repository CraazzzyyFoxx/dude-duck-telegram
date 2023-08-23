import re

import jinja2

from beanie import PydanticObjectId
from fastapi import HTTPException
from starlette import status

from app.core import config
from app.services.api import schemas as api_schemas

from . import service, models


def get_base_by_name(order: api_schemas.Order):
    return ["base", order.info.game, "eta-price"]


async def get(parser_id: PydanticObjectId):
    parser = await service.get(parser_id)
    if not parser:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A Render Config with this id does not exist."}],
        )
    return parser


async def get_by_name(name: str):
    parser = await service.get_by_name(name)
    if not parser:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": f"A Render Config with this name={name} does not exist."}],
        )
    return parser


async def create(parser_in: models.RenderConfigCreate):
    data = await service.get_by_name(parser_in.name)
    if data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": f"A Render Config with this name={parser_in.name} already exists"}],
        )
    return await service.create(parser_in)


async def update(name: str, parser_in: models.RenderConfigUpdate):
    data = await get_by_name(name)
    return await service.update(data, parser_in)


async def delete(name: str):
    parser = await get_by_name(name)
    return await service.delete(parser.id)


async def check_availability_all_render_config_order(order: api_schemas.Order):
    configs = await service.get_all_configs_for_order(order)
    names = service.get_all_config_names(order)
    exist_names = [config.name for config in configs]
    if len(configs) != len(names):
        missing = []
        for name in names:
            if name not in exist_names:
                missing.append(name)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": f"Some Render Configs for order missing configs=[{', '.join(missing)}]"}],
        )
    return True


def _render(pre_render: str):
    rendered = pre_render.replace("<br>", "\n")
    rendered = re.sub(" +", " ", rendered).replace(" .", ".").replace(" ,", ",")
    rendered = "\n".join(line.strip() for line in rendered.split("\n"))
    rendered = rendered.replace("{FOURSPACES}", "    ")
    return rendered


def _render_template(template_name: str, data: dict | None = None) -> str:
    template = _get_template_env().get_template(f"{template_name}.j2")
    if data is None:
        data = {}
    rendered = template.render(**data).replace("\n", " ")
    return _render(rendered)


def base(template_name: str, lang: api_schemas.UserLanguage, *, data: dict | None = None) -> str:
    return _render_template(f"{lang.value}/{template_name}", data)


def system(template_name: str, *, data: dict | None = None) -> str:
    template_name = f"system/{template_name}"
    return _render_template(template_name, data)


def user(template_name: str, user_in: api_schemas.User, *, data: dict | None = None) -> str:
    if data is not None:
        data["user"] = user_in
    else:
        data = {"user": user_in}
    template_name = f"{user_in.language.value}/{template_name}"
    return _render_template(template_name, data)


def _get_template_env():
    if not getattr(_get_template_env, "template_env", None):
        template_loader = jinja2.FileSystemLoader(searchpath=config.TEMPLATES_DIR)
        env = jinja2.Environment(
            loader=template_loader,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=True,
        )

        _get_template_env.template_env = env
    return _get_template_env.template_env


async def pre_order(templates: list[str], *, data: dict) -> str:
    resp = []
    for index, temp in enumerate(templates, 1):
        render_config = await get_by_name(temp)
        template = jinja2.Template(render_config.binary, trim_blocks=True, lstrip_blocks=True, autoescape=True)
        rendered = template.render(**data).replace("\n", " ")
        if not render_config.allow_separator_top and len(resp) > 0:
            resp.pop(-1)
        resp.append(rendered)
        if index < len(templates):
            resp.append(f"{render_config.separator}<br>")
    rendered = ''.join(resp)
    return rendered


async def order(templates: list[str], *, data: dict) -> str:
    return _render(await pre_order(templates, data=data))
