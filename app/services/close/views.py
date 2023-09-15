from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from aiogram.utils.web_app import WebAppInitData, safe_parse_webapp_init_data
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.core import errors
from app.core.bot import bot
from app.core.enums import RouteTag
from app.helpers import process_language
from app.services.api import flows as api_flows
from app.services.render import flows as render_flows

from . import flows, models

router = APIRouter(prefix='/order', tags=[RouteTag.CLOSE], include_in_schema=False)
templates = Jinja2Templates(directory="static")


async def response_web_query(init_data: WebAppInitData, title: str, message: str):
    await bot.answer_web_app_query(
        web_app_query_id=init_data.query_id,
        result=InlineQueryResultArticle(
            id=init_data.query_id,
            title=title,
            input_message_content=InputTextMessageContent(
                message_text=message,
                parse_mode="HTML",
            ),
        ),
    )


@router.get("/close", response_class=HTMLResponse)
async def read_items(request: Request, user_id: int):
    orders = await api_flows.get_me_orders(user_id, status=api_flows.models.OrderSelection.InProgress)
    return templates.TemplateResponse("close.html", {"request": request, "orders": orders.results})


@router.post("/close")
async def order_close(data: dict):
    try:
        init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    except ValueError:
        return ORJSONResponse({"ok": False, "err": "Unauthorized"}, status_code=401)
    try:
        user = await api_flows.get_me_user_id(init_data.user.id)
    except errors.AuthorizationExpired:
        lang = process_language(init_data.user)
        await response_web_query(init_data, "Order Close", render_flows.base("expired", lang))
        return ORJSONResponse({"ok": False, "err": "Unauthorized"}, status_code=401)

    try:
        valid = models.CloseOrderForm.model_validate(data)
    except ValidationError:
        await response_web_query(init_data, "Order Close", render_flows.user("order_close_422", user))
        return
    try:
        status = await flows.me_close_order(init_data.user.id, valid)
    except errors.AuthorizationExpired:
        lang = process_language(init_data.user)
        await response_web_query(init_data, "Order Close", render_flows.base("expired", lang))
        return ORJSONResponse({"ok": False, "err": "Unauthorized"}, status_code=401)
    if status == 201:
        await response_web_query(init_data, "Order Close", render_flows.user("order_close_201", user))
    if status == 403:
        await response_web_query(init_data, "Order Close", render_flows.user("order_close_403", user))
    return ORJSONResponse({"ok": True})
