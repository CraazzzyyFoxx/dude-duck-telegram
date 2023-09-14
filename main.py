import os
from contextlib import asynccontextmanager

import jinja2
from aiogram.types import BotCommandScopeAllPrivateChats
from aiogram_dialog import setup_dialogs
from aiogram_dialog.widgets.text import setup_jinja
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from starlette.staticfiles import StaticFiles
from tortoise import Tortoise, connections

from app.core import bot, config, enums
from app.core.extensions import configure_extensions
from app.core.logging import logger
from app.core.webhook import SimpleRequestHandler, setup_application
from app.handler import router as tg_router
from app.middlewares.exception import ExceptionMiddleware
from app.middlewares.time import TimeMiddleware
from app.routers import router
from app.services.api import service as api_service

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
        commands=enums.my_commands_ru, scope=BotCommandScopeAllPrivateChats(), language_code="ru")
    await bot.bot.set_my_commands(
        commands=enums.my_commands_en, scope=BotCommandScopeAllPrivateChats(), language_code="en")
    await bot.bot.set_webhook(url=f"{config.app.webhook_url}/bot/api/telegram/webhook",
                              secret_token=config.app.api_token,
                              drop_pending_updates=True)
    logger.info("Bot... Online!")
    yield
    await api_service.ApiService.shutdown()
    await bot.bot.session.close()
    await connections.close_all()


app = FastAPI(openapi_url="", lifespan=lifespan, default_response_class=ORJSONResponse, debug=config.app.debug)
app.add_middleware(ExceptionMiddleware)
app.add_middleware(TimeMiddleware)


api_app = FastAPI(title="DudeDuck CRM Telegram", root_path="/bot", debug=config.app.debug)
api_app.mount("/static", StaticFiles(directory="static"), name="static")
api_app.include_router(router)

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
                   allow_headers=["*"]
                   )

srh = SimpleRequestHandler(bot.dp, bot.bot, handle_in_background=False, _bot=bot.bot)
srh.register(api_app, "/api/telegram/webhook")
setup_application(api_app, bot.dp, _bot=bot.bot, bot=bot.bot)


app.mount("/bot", app=api_app)
