from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from aiogram.utils.web_app import WebAppInitData, safe_parse_webapp_init_data
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from app.core.bot import bot
from app.core.enums import RouteTag
from app.helpers import process_language
from app.services.render import flows as render_flows

from . import models, service

router = APIRouter(prefix="/auth", tags=[RouteTag.AUTH])
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
async def login(request: Request, message_id: int):
    return templates.TemplateResponse("login.html", {"request": request, "message_id": message_id})


@router.get("/signup", response_class=HTMLResponse)
async def signup(request: Request, message_id: int):
    return templates.TemplateResponse("signup.html", {"request": request, "message_id": message_id})


@router.post("/login")
async def login(data: dict):
    try:
        init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    except (ValueError, KeyError):
        return ORJSONResponse({"ok": False, "err": "Unauthorized"}, status_code=401)
    try:
        if data.get("message_id"):
            await bot.delete_message(init_data.user.id, data["message_id"])
    except:
        pass
    try:
        valid = models.LoginForm.model_validate(data)
    except ValidationError:
        lang = process_language(init_data.user, None)
        await response_web_query(init_data, "Login", render_flows.base("login_422", lang))
        return

    status, user = await service.login(init_data.user.id, valid.email, valid.password)

    if status == 200:
        await response_web_query(init_data, "Login", render_flows.user("login_200", user.user))
    elif status == 400:
        lang = process_language(init_data.user)
        await response_web_query(init_data, "Login", render_flows.base("login_400", lang))
    else:
        lang = process_language(init_data.user)
        await response_web_query(init_data, "Login", render_flows.base("auth_not_available", lang))
    return ORJSONResponse({"ok": True})


@router.post("/signup")
async def signup(data: dict):
    try:
        init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    except ValueError:
        return ORJSONResponse({"ok": False, "err": "Unauthorized"}, status_code=401)

    await bot.delete_message(init_data.user.id, data["message_id"])
    try:
        valid = models.SignInForm.model_validate(data)
    except ValidationError:
        lang = process_language(init_data.user, None)
        await response_web_query(init_data, "Sign Up", render_flows.base("register_422", lang))
        return

    if valid.password != valid.repeat_password:
        lang = process_language(init_data.user, None)
        await response_web_query(init_data, "Sign Up", render_flows.base("register_403", lang))
        return

    status, resp = await service.register(init_data.user.id, init_data.user.username, valid)
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
