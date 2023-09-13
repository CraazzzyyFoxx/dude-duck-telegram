import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from aiogram import Bot, Dispatcher
from aiogram.methods import TelegramMethod
from fastapi import Depends, FastAPI, Request, Response

from app.services.auth.bearers import requires_authorization_telegram


def setup_application(app: FastAPI, dispatcher: Dispatcher, /, **kwargs: Any) -> None:
    """
    This function helps to configure startup-shutdown process

    :param app:
    :param dispatcher:
    :param kwargs:
    :return:
    """
    workflow_data = {
        "app": app,
        "dispatcher": dispatcher,
        **kwargs,
        **dispatcher.workflow_data,
    }

    async def on_startup(*a: Any, **kw: Any) -> None:  # pragma: no cover
        await dispatcher.emit_startup(**workflow_data)

    async def on_shutdown(*a: Any, **kw: Any) -> None:  # pragma: no cover
        await dispatcher.emit_shutdown(**workflow_data)

    app.add_event_handler("startup", on_startup)
    app.add_event_handler("shutdown", on_shutdown)


class BaseRequestHandler(ABC):
    """
    Base handler that helps to handle incoming request from aiohttp
    and propagate it to the Dispatcher
    """

    def __init__(
            self, dispatcher: Dispatcher, handle_in_background: bool = True, **data: Any
    ) -> None:
        """
        :param dispatcher: instance of :class:`aiogram.dispatcher.dispatcher.Dispatcher`
        :param handle_in_background: immediately respond to the Telegram instead of waiting end of handler process
        """
        self.dispatcher = dispatcher
        self.handle_in_background = handle_in_background
        self.data = data

    def register(self, app: FastAPI, /, path: str, **kwargs: Any) -> None:
        """
        Register route and shutdown callback

        :param app: instance of aiohttp Application
        :param path: route path
        :param kwargs:
        """
        app.add_event_handler("shutdown", self._handle_close)
        app.add_api_route(path=path,
                          endpoint=self.handle,
                          methods=["POST"],
                          dependencies=[Depends(requires_authorization_telegram)],
                          include_in_schema=False,
                          )

    async def _handle_close(self) -> None:
        await self.close()

    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    async def resolve_bot(self, request: Request) -> Bot:
        pass

    async def _background_feed_update(self, bot: Bot, update: Dict[str, Any]) -> None:
        result = await self.dispatcher.feed_raw_update(bot=bot, update=update, **self.data)
        if isinstance(result, TelegramMethod):
            await self.dispatcher.silent_call_request(bot=bot, result=result)

    async def _handle_request_background(self, bot: Bot, request: Request) -> Response:
        asyncio.create_task(
            self._background_feed_update(
                bot=bot, update=bot.session.json_loads(await request.body())
            )
        )
        return Response(bot.session.json_dumps({}), media_type="application/json")

    async def _handle_request(self, bot: Bot, request: Request) -> Response:
        result = await self.dispatcher.feed_webhook_update(
            bot,
            bot.session.json_loads(await request.body()),
            **self.data,
        )
        if result:
            return Response(bot.session.json_dumps(result), media_type="application/json")

    async def handle(self, request: Request) -> Response:
        bot = await self.resolve_bot(request)
        if self.handle_in_background:
            return await self._handle_request_background(bot=bot, request=request)
        return await self._handle_request(bot=bot, request=request)

    __call__ = handle


class SimpleRequestHandler(BaseRequestHandler):

    def __init__(
            self, dispatcher: Dispatcher, bot: Bot, handle_in_background: bool = True, **data: Any
    ) -> None:
        super().__init__(dispatcher=dispatcher, handle_in_background=handle_in_background, **data)
        self.bot = bot

    async def close(self) -> None:
        await self.bot.session.close()

    async def resolve_bot(self, request: Request) -> Bot:
        return self.bot


class TokenBasedRequestHandler(BaseRequestHandler):
    """
    Handler that supports multiple bots, the context will be resolved from path variable 'bot_token'
    """

    def __init__(
            self,
            dispatcher: Dispatcher,
            handle_in_background: bool = True,
            bot_settings: Optional[Dict[str, Any]] = None,
            **data: Any,
    ) -> None:
        """
        :param dispatcher: instance of :class:`aiogram.dispatcher.dispatcher.Dispatcher`
        :param handle_in_background: immediately respond to the Telegram instead of waiting end of handler process
        :param bot_settings: kwargs that will be passed to new Bot instance
        """
        super().__init__(dispatcher=dispatcher, handle_in_background=handle_in_background, **data)
        if bot_settings is None:
            bot_settings = {}
        self.bot_settings = bot_settings
        self.bots: Dict[str, Bot] = {}

    async def close(self) -> None:
        for bot in self.bots.values():
            await bot.session.close()

    def register(self, app: FastAPI, /, path: str, **kwargs: Any) -> None:
        """
        Validate path, register route and shutdown callback

        :param app: instance of aiohttp Application
        :param path: route path
        :param kwargs:
        """
        if "{bot_token}" not in path:
            raise ValueError("Path should contains '{bot_token}' substring")
        super().register(app, path=path, **kwargs)

    async def resolve_bot(self, request: Request) -> Bot:
        """
        Get bot token from path and create or get from cache Bot instance

        :param request:
        :return:
        """
        token = request.path_params["bot_token"]
        if token not in self.bots:
            self.bots[token] = Bot(token=token, **self.bot_settings)
        return self.bots[token]
