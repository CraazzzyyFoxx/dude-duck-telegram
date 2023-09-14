from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import CallbackQuery, Message

from app.core import errors
from app.helpers import process_language
from app.services.api import flows as api_flows
from app.services.render import flows as render_flows


class PermissionMessageMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        user = await api_flows.get_me_user_id(event.from_user.id)
        data["user"] = user
        chat_action = get_flag(data, 'chat_action')
        if chat_action is not None:
            is_superuser = "is_superuser" in chat_action
            is_private = "is_private" in chat_action
            is_auth = "is_auth" in chat_action
        else:
            is_superuser = False
            is_private = False
            is_auth = False

        if is_auth and event.chat.type != "private":
            lang = process_language(event.from_user)
            await event.answer(render_flows.base("only_private", lang))
            return

        if is_auth:
            return await handler(event, data)

        user = await api_flows.get_me_user_id(event.from_user.id)

        if user is None:
            raise errors.AuthorizationExpired()

        if not user.is_verified:
            await event.answer(render_flows.user("verify_no", user))
            return

        if is_private and event.chat.type != "private":
            await event.answer(render_flows.user("only_private", user))
            return

        if is_superuser and not user.is_superuser:
            await event.answer(render_flows.user("missing_perms", user))
            return

        data['user'] = user
        return await handler(event, data)


class PermissionCallbackMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        user = await api_flows.get_me_user_id(event.from_user.id)
        data["user"] = user
        chat_action = get_flag(data, 'chat_action')
        if chat_action is not None:
            is_superuser = "is_superuser" in chat_action
            is_private = "is_private" in chat_action
            is_auth = "is_auth" in chat_action
        else:
            is_superuser = False
            is_private = False
            is_auth = False

        if is_auth:
            return await handler(event, data)

        user = await api_flows.get_me_user_id(event.from_user.id)

        if not user.is_verified:
            await event.answer(render_flows.user("verify_no", user), show_alert=True)
            return

        if is_private and event.message.chat.type != "private":
            await event.answer(render_flows.user("only_private", user), show_alert=True)
            return

        if is_superuser and not user.is_superuser:
            await event.answer(render_flows.user("missing_perms", user), show_alert=True)
            return

        data['user'] = user
        return await handler(event, data)
