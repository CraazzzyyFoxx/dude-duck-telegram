import os
from contextlib import asynccontextmanager

import jinja2
import sentry_sdk
import uvicorn

from aiogram_dialog import setup_dialogs
from aiogram_dialog.widgets.text import setup_jinja
from aiogram.types import BotCommandScopeAllPrivateChats
from beanie import init_beanie

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from starlette import status
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.staticfiles import StaticFiles

from app.core import bot, errors, config, enums
from app.core.logging import logger
from app.core.webhook import setup_application, SimpleRequestHandler
from app.middlewares.exception import ExceptionMiddleware
from app.middlewares.time import TimeMiddleware
from app.services.api import service as api_service
from app.handler import router as tg_router
from app.api import router
from app.db import get_beanie_models


@asynccontextmanager
async def lifespan(application: FastAPI):  # noqa
    client = AsyncIOMotorClient(config.app.mongo_dsn.unicode_string())
    await init_beanie(database=getattr(client, config.app.mongo_name), document_models=get_beanie_models())

    setup_dialogs(bot.dp)
    setup_jinja(bot.bot, loader=jinja2.FileSystemLoader(searchpath=config.TEMPLATES_DIR))
    bot.dp.include_router(tg_router)
    await api_service.ApiService.init()
    await bot.bot.set_my_commands(commands=enums.my_commands_ru, scope=BotCommandScopeAllPrivateChats(), language_code="ru")
    await bot.bot.set_my_commands(commands=enums.my_commands_en, scope=BotCommandScopeAllPrivateChats(), language_code="en")
    await bot.bot.set_webhook(url=f"{config.app.webhook_url}/api/telegram/webhook",
                              secret_token=config.app.api_token,
                              drop_pending_updates=True)
    logger.info("Bot... Online!")
    yield
    await api_service.ApiService.shutdown()
    await bot.bot.session.close()


app = FastAPI(
    lifespan=lifespan,
    debug=False,
    default_response_class=ORJSONResponse,
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Validation Error",
            "model": errors.APIValidationError,
        }
    },
)
app.add_middleware(TimeMiddleware)
app.add_middleware(ExceptionMiddleware)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(router)

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
                   allow_headers=["*"]
                   )

srh = SimpleRequestHandler(bot.dp, bot.bot, handle_in_background=False, _bot=bot.bot)
srh.register(app, "/api/telegram/webhook")
setup_application(app, bot.dp, _bot=bot.bot, bot=bot.bot)

if not config.app.debug:
    sentry_sdk.init(
        dsn=config.app.sentry_dsn,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0
    )


if __name__ == '__main__':
    if os.name != "nt":
        import uvloop  # noqa

        uvloop.install()

    uvicorn.run(
        "main:app",
        host=config.app.host,
        port=config.app.port,
        ssl_keyfile='key.pem',
        ssl_certfile='cert.pem'
    )
