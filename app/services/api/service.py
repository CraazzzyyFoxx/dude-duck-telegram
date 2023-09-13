import typing
from datetime import datetime, timedelta

import pytz
from httpx import AsyncClient, TimeoutException, HTTPError, Response
from fastapi.encoders import jsonable_encoder
from loguru import logger

from app.core import config, errors

from . import models


class ApiServiceMeta:
    __slots__ = ("client", )

    def __init__(self):
        self.client = AsyncClient(timeout=8)

    @staticmethod
    def _build_client() -> AsyncClient:
        return AsyncClient()

    async def init(self) -> None:
        if self.client.is_closed:
            self.client = self._build_client()

    async def shutdown(self) -> None:
        if self.client.is_closed:
            logger.debug("This HTTPXRequest is already shut down. Returning.")
            return

        await self.client.aclose()


ApiService = ApiServiceMeta()


async def get(user_id: int) -> models.TelegramUser | None:
    return await models.TelegramUser.filter(id=user_id).first()


async def get_by_user_id(user_id: str) -> list[models.TelegramUser]:
    return await models.TelegramUser.filter(user_id=user_id).all()


async def get_by_telegram_user_id(user_id: int) -> models.TelegramUser | None:
    return await models.TelegramUser.filter(telegram_user_id=user_id).first()


async def create(user_order_in: models.TelegramUserCreate) -> models.TelegramUser:
    return await models.TelegramUser.create(
        **user_order_in.model_dump()
    )


async def delete(user_id: id):
    user_order = await models.TelegramUser.get(user_id)
    if user_order:
        await user_order.delete()


async def update(user: models.TelegramUser, user_in: models.TelegramUserUpdate) -> models.TelegramUser:
    user.token = user_in.token
    if user_in.user:
        user.user = user_in.user.model_dump()
        user.last_update = datetime.utcnow()
        user.last_login = user_in.last_login

    await user.save()
    return user


async def get_token(user_id: int) -> str | None:
    user = await get(user_id)
    if user is None:
        return None
    if user.last_login > (datetime.now() - timedelta(days=1)).astimezone(pytz.UTC):
        return None
    return user.token


async def get_token_user_id(user_id: int) -> str | None:
    user = await get_by_telegram_user_id(user_id)
    if user is None:
        return None
    if user.last_login is None or user.last_login < (datetime.now() - timedelta(days=1)).astimezone(pytz.UTC):
        return None
    return user.token


async def request(
        url: str,
        method: typing.Literal["GET", "POST", "PATCH", "DELETE"],
        token: str | None,
        *,
        json: typing.Any = None,
        data: dict = None
) -> Response:
    if token is None:
        raise errors.AuthorizationExpired()
    try:
        response = await ApiService.client.request(
            method=method,
            url=f"{config.app.backend_url}api/v1/{url}",
            json=jsonable_encoder(json) if json is not None else None,
            data=data,
            headers={"Authorization": "Bearer " + token} if token else None,
        )
    except TimeoutException:
        raise errors.ServerNotResponseError()
    except HTTPError:
        raise errors.InternalServerError()
    else:
        if response.status_code == 401:
            raise errors.AuthorizationExpired()
        if response.status_code == 422:
            raise errors.InternalServerError()
        if response.status_code == 500:
            raise errors.InternalServerError()

        return response


async def request_auth(
        url: str,
        method: typing.Literal["GET", "POST", "PUT", "DELETE"],
        *,
        token: str | None = None,
        json: typing.Any = None,
        data: dict = None
) -> Response:
    try:
        response = await ApiService.client.request(
            method=method,
            url=f"{config.app.backend_url}{url}",
            json=jsonable_encoder(json) if json is not None else None,
            data=data,
            headers={"Authorization": "Bearer " + token} if token else None,
        )
    except TimeoutException:
        raise errors.ServerNotResponseError()
    except HTTPError:
        raise errors.InternalServerError()
    else:
        if response.status_code == 500:
            raise errors.InternalServerError()
        return response
