from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from aiogram.utils.web_app import WebAppInitData
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from src.core import db, errors
from src.core.bot import bot
from src import schemas
from src.core.enums import RouteTag
from src.helpers import process_language
from src.services.api import flows as api_flows
from src.services.api import service as api_service
from src.services.render import flows as render_flows
from src.utils.web_query import validate_webapp_init_data

from . import flows

router = APIRouter(prefix="/order", tags=[RouteTag.CLOSE], include_in_schema=False)
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
async def read_items(
    request: Request,
    user_id: int,
    session: AsyncSession = Depends(db.get_async_session),
):
    user_db = await api_service.get_by_telegram(session, user_id)
    orders = await api_flows.get_me_orders(user_db, status=api_flows.models.OrderSelection.InProgress)
    return templates.TemplateResponse("close.html", {"request": request, "orders": orders.results})


@router.post("/close")
async def order_close(
    data: dict,
    session: AsyncSession = Depends(db.get_async_session),
    init_data: WebAppInitData = Depends(validate_webapp_init_data),
):
    try:
        user_db = await api_service.get_by_telegram(session, init_data.user.id)
    except errors.AuthorizationExpired:
        lang = process_language(init_data.user)
        await response_web_query(init_data, "Order Close", render_flows.base("expired", lang))
        return ORJSONResponse({"ok": False, "err": "Unauthorized"}, status_code=401)

    try:
        valid = schemas.CloseOrderForm.model_validate(data)
    except ValidationError:
        await response_web_query(init_data, "Order Close", render_flows.user("order_close_422", user_db))
        return
    try:
        status = await flows.me_close_order(user_db, valid)
    except errors.AuthorizationExpired:
        lang = process_language(init_data.user)
        await response_web_query(init_data, "Order Close", render_flows.base("expired", lang))
        return ORJSONResponse({"ok": False, "err": "Unauthorized"}, status_code=401)
    if status == 201:
        await response_web_query(init_data, "Order Close", render_flows.user("order_close_201", user_db))
    if status == 403:
        await response_web_query(init_data, "Order Close", render_flows.user("order_close_403", user_db))
    return ORJSONResponse({"ok": True})
