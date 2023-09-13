import aiogram_dialog

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent
from aiogram_dialog import DialogManager
from aiogram_dialog.api.exceptions import UnknownIntent
from loguru import logger

from app.core import config, errors
from app.middlewares.permissions import PermissionMessageMiddleware, PermissionCallbackMiddleware
from app.services.render import flows as render_flows
from app.helpers import process_language


bot = Bot(token=config.app.token, parse_mode="HTML")
dp = Dispatcher()

dp.message.middleware(PermissionMessageMiddleware())
dp.callback_query.middleware(PermissionCallbackMiddleware())


@dp.error(ExceptionTypeFilter(errors.AuthorizationExpired))
async def handle_message_expired_error(event: ErrorEvent, user=None, dialog_manager=None):
    try:
        await dialog_manager.done()
    except aiogram_dialog.api.exceptions.NoContextError:
        pass
    if event.update.callback_query is not None:
        lang = process_language(event.update.callback_query.from_user, user)
        await event.update.callback_query.answer(render_flows.base("expired", lang), show_alert=True)
    if event.update.message is not None:
        lang = process_language(event.update.message.from_user, user)
        await event.update.message.answer(render_flows.base("expired", lang))


@dp.error(ExceptionTypeFilter(UnknownIntent))
async def on_unknown_intent(event: ErrorEvent, dialog_manager: DialogManager, user=None):
    if event.update.callback_query:
        lang = process_language(event.update.callback_query.from_user, user)
        await event.update.callback_query.answer(render_flows.base("menu_restarted", lang))
        try:
            await event.update.callback_query.message.delete()
        except TelegramBadRequest:
            pass
    try:
        await dialog_manager.done()
    except aiogram_dialog.api.exceptions.NoContextError:
        pass


@dp.error(ExceptionTypeFilter(errors.InternalServerError, errors.ServerNotResponseError, Exception))
async def handle_message_server_error(event: ErrorEvent, user=None, dialog_manager=None):
    try:
        await dialog_manager.done()
    except aiogram_dialog.api.exceptions.NoContextError:
        pass
    if event.update.callback_query is not None:
        lang = process_language(event.update.callback_query.from_user, user)
        await event.update.callback_query.answer(render_flows.base("internal_error", lang), show_alert=True)
    if event.update.message is not None:
        lang = process_language(event.update.message.from_user, user)
        await event.update.message.answer(render_flows.base("internal_error", lang))
    try:
        raise event.exception
    except:
        logger.exception("Прогер долбаеб....")
