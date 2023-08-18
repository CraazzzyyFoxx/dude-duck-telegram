import re

import jinja2

from app.core import config
from app.services.api import schemas as api_schemas


def _render_template(template_name: str, data: dict | None = None) -> str:
    template = _get_template_env().get_template(f"{template_name}.j2")
    if data is None:
        data = {}
    rendered = template.render(**data).replace("\n", " ")
    rendered = rendered.replace("<br>", "\n")
    rendered = re.sub(" +", " ", rendered).replace(" .", ".").replace(" ,", ",")
    rendered = "\n".join(line.strip() for line in rendered.split("\n"))
    rendered = rendered.replace("{FOURPACES}", "    ")
    return rendered


def render_template(template_name: str, lang: api_schemas.UserLanguage,  *, data: dict | None = None) -> str:
    return _render_template(f"{lang.value}/{template_name}", data)


def render_template_system(template_name: str, *, data: dict | None = None) -> str:
    template_name = f"system/{template_name}"
    return _render_template(template_name, data)


def render_template_user(template_name: str, user: api_schemas.User, *, data: dict | None = None) -> str:
    if data:
        data["user"] = user
    else:
        data = {"user": user}

    template_name = f"{user.language.value}/{template_name}"
    return _render_template(template_name, data)


def _get_template_env():
    if not getattr(_get_template_env, "template_env", None):
        template_loader = jinja2.FileSystemLoader(searchpath=config.TEMPLATES_DIR)
        env = jinja2.Environment(
            loader=template_loader,
            trim_blocks=True,
            lstrip_blocks=True,
            # autoescape=True,
        )

        _get_template_env.template_env = env

    return _get_template_env.template_env
