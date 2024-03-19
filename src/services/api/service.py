import typing

import sqlalchemy as sa
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient, HTTPError, Response, TimeoutException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import config, errors
from src import models

api_client = AsyncClient(
    timeout=8,
    verify=False,
    base_url=f"{config.app.backend_url}api/v1",
    headers={"User-Agent": "TelegramBot"}
)


async def get_by_user_id(session: AsyncSession, user_id: int) -> models.UserDB | None:
    query = sa.select(models.UserDB).where(models.UserDB.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().first()


async def get_by_telegram(session: AsyncSession, user_id: int) -> models.UserDB | None:
    query = sa.select(models.UserDB).where(models.UserDB.telegram_user_id == user_id)
    result = await session.execute(query)
    return result.scalars().first()


async def get_by_telegram_user_id(session: AsyncSession, user_id: int, telegram_id: int) -> models.UserDB | None:
    query = sa.select(models.UserDB).where(
        models.UserDB.telegram_user_id == telegram_id, models.UserDB.user_id == user_id
    )
    result = await session.execute(query)
    return result.scalars().first()


async def create(session: AsyncSession, user_order_in: models.UserCreate) -> models.UserDB:
    user_order = models.UserDB(**user_order_in.model_dump(mode="json"))
    session.add(user_order)
    await session.commit()
    return user_order


async def update(session: AsyncSession, user: models.UserDB, user_in: models.UserUpdate) -> models.UserDB:
    update_model = user_in.model_dump(exclude_unset=True)
    if user_in.user_json:
        update_model["user_json"] = user_in.user_json.model_dump(mode="json")
    query = (
        sa.update(models.UserDB)
        .where(models.UserDB.telegram_user_id == user.telegram_user_id, models.UserDB.user_id == user.user_id)
        .values(update_model)
        .returning(models.UserDB)
    )
    result = await session.scalars(query)
    await session.commit()
    return result.one()


async def request(
        url: str,
        method: typing.Literal["GET", "POST", "PATCH", "DELETE"],
        token: str | None,
        *,
        json: typing.Any = None,
        data: dict | None = None,
) -> Response:
    if token is None:
        raise errors.AuthorizationExpired()
    try:
        response = await api_client.request(
            method=method,
            url=url,
            json=jsonable_encoder(json) if json is not None else None,
            data=data,
            headers={"Authorization": "Bearer " + token} if token else None,
        )
    except TimeoutException:
        raise errors.ServerNotResponseError() from None
    except HTTPError:
        raise errors.InternalServerError() from None
    else:
        if response.status_code == 401:
            raise errors.AuthorizationExpired()
        if response.status_code == 422:
            logger.warning(response.json())
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
        data: dict | None = None,
) -> Response:
    try:
        response = await api_client.request(
            method=method,
            url=f"{url}",
            json=jsonable_encoder(json) if json is not None else None,
            data=data,
            headers={"Authorization": "Bearer " + token} if token else None,
        )
    except TimeoutException:
        raise errors.ServerNotResponseError() from None
    except HTTPError:
        raise errors.InternalServerError() from None
    else:
        if response.status_code == 500:
            raise errors.InternalServerError()
        return response
