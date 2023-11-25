import re

import jinja2

from src.core import config
from src.services.api import schemas as api_schemas
from src.services.api import service as api_service


def _render(pre_render: str) -> str:
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


def _get_template_env() -> jinja2.Environment:
    if not getattr(_get_template_env, "template_env", None):
        template_loader = jinja2.FileSystemLoader(searchpath=config.TEMPLATES_DIR)
        env = jinja2.Environment(
            loader=template_loader,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        _get_template_env.template_env = env
    return _get_template_env.template_env


async def get_order_text(
    user_id: int,
    order_id: int,
    is_preorder: bool = False,
    is_gold: bool = False,
    with_credentials: bool = False,
    with_response: bool = False,
    response_checked: bool = False,
    response_user_id: int | None = None,
) -> str:
    url = (
        f"integrations/render/order"
        f"?order_id={order_id}"
        f"&integration=telegram"
        f"&is_preorder={is_preorder}"
        f"&is_gold={is_gold}"
        f"&with_credentials={with_credentials}"
        f"&with_response={with_response}"
        f"&response_checked={response_checked}"
    )
    if response_user_id:
        url += f"&user_id={response_user_id}"
    resp = await api_service.request(url.lower(), "GET", await api_service.get_token_user_id(user_id))
    if resp.status_code == 200:
        return resp.json()["text"]
    elif resp.status_code == 400:
        return resp.json()["detail"][0]["msg"]
    elif resp.status_code == 404:
        return "Order not found"
