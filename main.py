import os
from contextlib import asynccontextmanager

import jinja2
from aiogram.types import BotCommandScopeAllPrivateChats
from aiogram_dialog import setup_dialogs
from aiogram_dialog.widgets.text import setup_jinja
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from starlette.staticfiles import StaticFiles
from tortoise import Tortoise, connections

from src.core import bot, config, enums
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
    await Tortoise.init(config=config.tortoise)
    await Tortoise.generate_schemas()
    setup_dialogs(bot.dp)
    setup_jinja(bot.bot, loader=jinja2.FileSystemLoader(searchpath=config.TEMPLATES_DIR))
    bot.dp.include_router(tg_router)
    await api_service.ApiService.init()
    await bot.bot.set_my_commands(
        commands=enums.my_commands_ru, scope=BotCommandScopeAllPrivateChats(), language_code="ru"
    )
    await bot.bot.set_my_commands(
        commands=enums.my_commands_en, scope=BotCommandScopeAllPrivateChats(), language_code="en"
    )
    await bot.bot.set_webhook(
        url=f"{config.app.webhook_url}/bot/api/telegram/webhook",
        secret_token=config.app.api_token,
        drop_pending_updates=True,
    )
    logger.info("Bot... Online!")
    yield
    await api_service.ApiService.shutdown()
    await bot.bot.session.close()
    await connections.close_all()


app = FastAPI(openapi_url="", lifespan=lifespan, default_response_class=ORJSONResponse, debug=config.app.debug)
app.add_middleware(ExceptionMiddleware)
app.add_middleware(SentryAsgiMiddleware)
app.add_middleware(TimeMiddleware)


api_app = FastAPI(title="DudeDuck CRM Telegram", root_path="/bot", debug=config.app.debug)
api_app.mount("/static", StaticFiles(directory="static"), name="static")
api_app.include_router(router)
api_app.add_middleware(ExceptionMiddleware)
app.add_middleware(SentryAsgiMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["*"],
)

srh = SimpleRequestHandler(bot.dp, bot.bot, handle_in_background=False, _bot=bot.bot)
srh.register(api_app, "/api/telegram/webhook")
setup_application(api_app, bot.dp, _bot=bot.bot, bot=bot.bot)


app.mount("/bot", app=api_app)
