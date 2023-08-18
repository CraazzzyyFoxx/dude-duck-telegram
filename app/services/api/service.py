import typing
from datetime import datetime, timedelta

from beanie import PydanticObjectId
from httpx import AsyncClient, TimeoutException, HTTPError, Response
from fastapi.encoders import jsonable_encoder
from loguru import logger

from app.core import config, errors

from . import models


class ApiServiceMeta:
    __slots__ = ("client", "_client_kwargs")

    def __init__(self):
        self.client = AsyncClient(timeout=8)

    def _build_client(self) -> AsyncClient:
        return AsyncClient(**self._client_kwargs)

    async def init(self) -> None:
        if self.client.is_closed:
            self.client = self._build_client()

    async def shutdown(self) -> None:
        if self.client.is_closed:
            logger.debug("This HTTPXRequest is already shut down. Returning.")
            return

        await self.client.aclose()


ApiService = ApiServiceMeta()


async def get(user_id: PydanticObjectId) -> models.TelegramUser:
    return await models.TelegramUser.find_one({"_id": user_id})


async def get_by_user_id(user_id: PydanticObjectId) -> models.TelegramUser:
    return await models.TelegramUser.find_one({"user_id": user_id})


async def get_by_telegram_user_id(user_id: int) -> models.TelegramUser:
    return await models.TelegramUser.find_one({"telegram_user_id": user_id})


async def create(user_order_in: models.TelegramUserCreate):
    user_order = models.TelegramUser(**user_order_in.model_dump())
    return await user_order.create()


async def delete(user_order_id: PydanticObjectId):
    user_order = await models.TelegramUser.get(user_order_id)
    if user_order:
        await user_order.delete()


async def update(user: models.TelegramUser, user_in: models.TelegramUserUpdate):
    user_data = user.model_dump()
    update_data = user_in.model_dump(exclude_none=True)

    for field in user_data:
        if field in update_data:
            setattr(user, field, update_data[field])

    await user.save_changes()
    return user


async def get_token(user_id: PydanticObjectId) -> str | None:
    user = await get(user_id)
    if user.last_login > datetime.utcnow() - timedelta(days=1):
        return None
    return user.token


async def get_token_user_id(user_id: int) -> str | None:
    user = await get_by_telegram_user_id(user_id)
    if user.last_login < datetime.utcnow() - timedelta(days=1):
        return None
    return user.token


async def request(
        url: str,
        method: typing.Literal["GET", "POST", "PUT", "DELETE"],
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
