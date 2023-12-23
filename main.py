import os
from contextlib import asynccontextmanager

import jinja2
from aiogram.types import BotCommandScopeAllPrivateChats
from aiogram_dialog import setup_dialogs
from aiogram_dialog.widgets.text import setup_jinja
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.staticfiles import StaticFiles

from src.core import bot, config, db, enums
from src.core.extensions import configure_extensions
from src.core.logging import logger
from src.core.webhook import SimpleRequestHandler, setup_application
from src.handler import router as tg_router
from src.middlewares.exception import ExceptionMiddleware
from src.middlewares.time import TimeMiddleware
from src.routers import router
from src.services.api import service as api_service

configure_extensions()

if os.name != "nt":
    import uvloop  # noqa

    uvloop.install()


@asynccontextmanager
async def lifespan(application: FastAPI):  # noqa
    db.Base.metadata.create_all(db.engine)
    setup_dialogs(bot.dp)
    setup_jinja(bot.bot, loader=jinja2.FileSystemLoader(searchpath=config.TEMPLATES_DIR))
    bot.dp.include_router(tg_router)
    await bot.bot.set_my_commands(
        commands=enums.my_commands_ru,
        scope=BotCommandScopeAllPrivateChats(),
        language_code="ru",
    )
    await bot.bot.set_my_commands(
        commands=enums.my_commands_en,
        scope=BotCommandScopeAllPrivateChats(),
        language_code="en",
    )
    await bot.bot.set_webhook(
        url=f"{config.app.webhook_url}/telegram/api/telegram/webhook",
        secret_token=config.app.api_token,
        drop_pending_updates=True,
    )
    logger.info("Bot... Online!")
    yield
    await api_service.api_client.aclose()
    await bot.bot.session.close()


async def not_found(request: Request, _: Exception):
    return ORJSONResponse(status_code=404, content={"detail": [{"msg": "Not Found"}]})


exception_handlers = {404: not_found}

app = FastAPI(
    openapi_url="",
    lifespan=lifespan,
    default_response_class=ORJSONResponse,
    debug=config.app.debug,
    exception_handlers=exception_handlers,
)
app.add_middleware(ExceptionMiddleware)
app.add_middleware(SentryAsgiMiddleware)
app.add_middleware(TimeMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.mount("/static", StaticFiles(directory="static"), name="static")

api_app = FastAPI(
    title="DudeDuck CRM Telegram",
    root_path="/telegram",
    debug=config.app.debug,
    exception_handlers=exception_handlers,
)
api_app.include_router(router)
api_app.add_middleware(ExceptionMiddleware)
api_app.add_middleware(GZipMiddleware, minimum_size=1000)


@api_app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):

    return ORJSONResponse(
        status_code=422,
        content={
            "detail": [
                {
                    "msg": jsonable_encoder(exc.errors(), exclude={"url", "type", "ctx"}),
                    "code": "unprocessable_entity",
                }
            ]
        },
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=config.app.cors_origins if config.app.cors_origins else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PATCH", "PUT"],
    allow_headers=["*"],
)

srh = SimpleRequestHandler(bot.dp, bot.bot, handle_in_background=False, _bot=bot.bot)
srh.register(api_app, "/api/telegram/webhook")
setup_application(api_app, bot.dp, _bot=bot.bot, bot=bot.bot)


app.mount("/telegram", app=api_app)
