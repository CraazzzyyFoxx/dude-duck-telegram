from aiogram.types import InlineQueryResultArticle, InputTextMessageContent
from aiogram.utils.web_app import safe_parse_webapp_init_data, WebAppInitData
from fastapi import APIRouter
from fastapi.responses import ORJSONResponse
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from pydantic import ValidationError

from app.core import enums
from app.core.bot import bot
from app.services.api import flows as api_flows
from app.services.api import schemas as api_schemas
from app.services.render import flows as render_flows

router = APIRouter(prefix='/users', tags=[enums.RouteTag.USERS])
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
async def read_users(request: Request, user_id: int):
    users = await api_flows.get_users(user_id)
    return templates.TemplateResponse("user_update.html", {"request": request, "users": users.results})


@router.post('/get/{user_id}')
async def read_user(user_id: str, data: dict):
    try:
        init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    except ValueError:
        return ORJSONResponse({"ok": False, "err": "Unauthorized"}, status_code=401)

    return await api_flows.get_user(init_data.user.id, user_id)


@router.post('/update/{user_id}')
async def update_user(user_id: str, data: dict):
    try:
        init_data = safe_parse_webapp_init_data(token=bot.token, init_data=data["_auth"])
    except ValueError:
        return ORJSONResponse({"ok": False, "err": "Unauthorized"}, status_code=401)
    try:
        payload = api_schemas.UserUpdate.model_validate(data)
    except ValidationError as error:
        msg = []
        for e in error.errors(include_url=False, include_context=False):
            try:
                msg.append(f"{e['loc'][0]} - {e['msg']}")
            except IndexError:
                msg.append(e['msg'])
        await response_web_query(init_data, "Users", '\n'.join(msg))
        return
    user = await api_flows.update_user(init_data.user.id, user_id, payload)
    await response_web_query(init_data, "Users", render_flows.user("user", user))
