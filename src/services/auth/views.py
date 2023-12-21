from aiogram.exceptions import TelegramAPIError
from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from aiogram.utils.web_app import WebAppInitData
from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from src.core import db, enums
from src.core.bot import bot
from src import schemas
from src.helpers import process_language
from src.services.render import flows as render_flows

from src.utils.web_query import validate_webapp_init_data
from . import service

router = APIRouter(prefix="/auth", tags=[enums.RouteTag.AUTH])
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


@router.get("/login", response_class=HTMLResponse)
async def login_template(request: Request, message_id: int):
    return templates.TemplateResponse("login.html", {"request": request, "message_id": message_id})


@router.get("/signup", response_class=HTMLResponse)
async def signup_template(request: Request, message_id: int):
    return templates.TemplateResponse("signup.html", {"request": request, "message_id": message_id})


@router.post("/login")
async def login(
    data: dict,
    session: AsyncSession = Depends(db.get_async_session),
    init_data: WebAppInitData = Depends(validate_webapp_init_data),
):
    try:
        if data.get("message_id"):
            await bot.delete_message(init_data.user.id, data["message_id"])
    except TelegramAPIError:
        pass
    try:
        valid = schemas.LoginForm.model_validate(data)
    except ValidationError:
        lang = process_language(init_data.user, None)
        await response_web_query(init_data, "Login", render_flows.base("login_422", lang))
        return

    status, user = await service.login(session, init_data.user, valid.email, valid.password)

    if status == 200:
        await response_web_query(init_data, "Login", render_flows.user("login_200", user))
    elif status == 400:
        lang = process_language(init_data.user)
        await response_web_query(init_data, "Login", render_flows.base("login_400", lang))
    else:
        lang = process_language(init_data.user)
        await response_web_query(init_data, "Login", render_flows.base("auth_not_available", lang))
    return ORJSONResponse({"ok": True})


@router.post("/signup")
async def signup(
    data: dict,
    session: AsyncSession = Depends(db.get_async_session),
    init_data: WebAppInitData = Depends(validate_webapp_init_data),
):
    try:
        if data.get("message_id"):
            await bot.delete_message(init_data.user.id, data["message_id"])
    except TelegramAPIError:
        pass
    try:
        valid = schemas.SignInForm.model_validate(data)
    except ValidationError:
        lang = process_language(init_data.user, None)
        await response_web_query(init_data, "Sign Up", render_flows.base("register_422", lang))
        return

    if valid.password != valid.repeat_password:
        lang = process_language(init_data.user, None)
        await response_web_query(init_data, "Sign Up", render_flows.base("register_403", lang))
        return

    status, resp = await service.register(session, init_data.user, valid)
    lang = process_language(init_data.user, None)
    if status == 400:
        await response_web_query(init_data, "Sign Up", render_flows.base("register_400", lang))
    if status == 201:
        await response_web_query(init_data, "Sign Up", render_flows.base("register_201", lang))
    if status == 500:
        await response_web_query(init_data, "Sign Up", render_flows.base("auth_not_available", lang))
    if status == 422:
        await response_web_query(init_data, "Sign Up", render_flows.base("register_422", lang))
    return ORJSONResponse({"ok": True})
