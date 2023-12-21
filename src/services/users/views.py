from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from aiogram.utils.web_app import WebAppInitData, safe_parse_webapp_init_data
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from src.core import db, enums
from src import schemas
from src.core.bot import bot
from src.services.api import flows as api_flows
from src.services.api import service as api_service
from src.services.render import flows as render_flows
from src.utils.web_query import validate_webapp_init_data

router = APIRouter(prefix="/users", tags=[enums.RouteTag.USERS])
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


@router.get("/", response_class=HTMLResponse)
async def read_users(
    request: Request,
    user_id: int,
    session: AsyncSession = Depends(db.get_async_session),
):
    user_db = await api_service.get_by_user_id(session, user_id)
    users = await api_flows.get_users(user_db)
    return templates.TemplateResponse("user_update.html", {"request": request, "users": users.results})


@router.post("/get/{user_id}")
async def read_user(user_id: int, data: dict, session: AsyncSession = Depends(db.get_async_session)):
    try:
        init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    except (ValueError, KeyError):
        return ORJSONResponse({"ok": False, "err": "Unauthorized"}, status_code=401)
    user_db = await api_service.get_by_user_id(session, init_data.user.id)
    return await api_flows.get_user(user_db, user_id)


@router.post("/update/{user_id}")
async def update_user(
    user_id: int,
    data: dict,
    session: AsyncSession = Depends(db.get_async_session),
    init_data: WebAppInitData = Depends(validate_webapp_init_data),
):
    try:
        payload = schemas.UserUpdate.model_validate(data)
    except ValidationError as error:
        msg = []
        for e in error.errors(include_url=False, include_context=False):
            try:
                msg.append(f"{e['loc'][0]} - {e['msg']}")
            except IndexError:
                msg.append(e["msg"])
        await response_web_query(init_data, "Users", "\n".join(msg))
        return
    user_db = await api_service.get_by_telegram(session, init_data.user.id)
    user = await api_flows.update_user(user_db, user_id, payload)
    await response_web_query(init_data, "Users", render_flows.user("user", user))
    return ORJSONResponse({"ok": True})
