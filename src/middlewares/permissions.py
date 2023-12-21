from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.dispatcher.flags import get_flag
from aiogram.types import CallbackQuery, Message, TelegramObject

from src.core import errors
from src import models
from src.helpers import process_language
from src.services.api import flows as api_flows
from src.services.api import service as api_service
from src.services.render import flows as render_flows


class PermissionMessageMiddleware(BaseMiddleware):
    @staticmethod
    async def send_template(event: TelegramObject, template_name: str, user: models.UserDB | None = None) -> None:
        kwargs = {}
        if isinstance(event, CallbackQuery):
            kwargs.update({"show_alert": True})
        if user is not None:
            text = render_flows.user(template_name, user)
        else:
            lang = process_language(event.from_user)
            text = render_flows.base(template_name, lang)
        await event.answer(text, **kwargs)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        data["user"] = None
        session = data["session"]
        chat_action = get_flag(data, "chat_action", default={})
        is_superuser = "is_superuser" in chat_action
        is_private = "is_private" in chat_action
        is_auth = "is_auth" in chat_action
        is_verify = "is_verify" in chat_action

        if is_private and event.chat.type != "private":
            return await self.send_template(event, "only_private")
        if is_auth:
            return await handler(event, data)
        try:
            user = await api_service.get_by_telegram(session, event.from_user.id)
            if user is None:
                return await self.send_template(event, "expired")
            await api_flows.get_me(session, user)
            data["user"] = user
        except errors.AuthorizationExpired:
            return await self.send_template(event, "expired")
        if user is None:
            return await self.send_template(event, "expired")
        if is_verify:
            return await handler(event, data)
        if not user.user.is_verified:
            return await self.send_template(event, "verify_no")
        if is_superuser and not user.user.is_superuser:
            return await self.send_template(event, "missing_perms")

        return await handler(event, data)
