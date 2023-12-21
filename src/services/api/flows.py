from datetime import datetime, timedelta

import pytz
from aiogram.utils.web_app import WebAppUser
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import pagination
from src import models, schemas

from . import service


async def get_me_login(token: str) -> schemas.UserWithPayrolls | None:
    resp = await service.request("users/@me", "GET", token)
    if resp.status_code == 200:
        return schemas.UserWithPayrolls.model_validate(resp.json())


async def get_me(session: AsyncSession, user_db: models.UserDB) -> schemas.UserWithPayrolls:
    if user_db.updated_at is not None and user_db.updated_at > (datetime.utcnow() - timedelta(minutes=5)).astimezone(
        pytz.UTC
    ):
        return user_db.user
    resp = await service.request("users/@me", "GET", user_db.get_token())
    if resp.status_code == 200:
        user = schemas.UserWithPayrolls.model_validate(resp.json())
        await service.update(session, user_db, models.UserUpdate(user_json=user))
        return user


async def connect_telegram(user_db: models.UserDB, user: WebAppUser) -> int:
    resp = await service.request(
        f"users/@me/telegram",
        "POST",
        user_db.get_token(),
        json={
            "account_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
        },
    )
    return resp.status_code


async def get_me_orders(
    user_db: models.UserDB, status: models.OrderSelection, page: int = 1
) -> pagination.Paginated[schemas.OrderRead]:
    resp = await service.request(
        f"users/@me/orders?page={page}&per_page=10&sort=created_at&order=asc&status={status.value}",
        "POST",
        user_db.get_token(),
    )
    return pagination.Paginated[schemas.OrderRead].model_validate(resp.json())


async def get_me_order(user_db: models.UserDB, order_id: int) -> schemas.OrderRead:
    resp = await service.request(f"users/@me/orders?order_id={order_id}", "GET", user_db.get_token())
    return schemas.OrderRead.model_validate(resp.json())


async def get_me_accounting(user_db: models.UserDB) -> dict | None:
    resp = await service.request("users/@me/payment/report", "GET", user_db.get_token())
    if resp.status_code == 200:
        return resp.json()
    return None


async def get_order(user_db: models.UserDB, order_id: int) -> schemas.Order:
    resp = await service.request(f"orders?order_id={order_id}", "GET", user_db.get_token())
    return schemas.Order.model_validate(resp.json())


async def get_preorder(user_db: models.UserDB, order_id: int) -> schemas.PreOrder:
    resp = await service.request(f"preorders?order_id={order_id}", "GET", user_db.get_token())
    return schemas.PreOrder.model_validate(resp.json())


async def change_language(session: AsyncSession, user_id: int) -> models.UserDB:
    me = await service.get_by_telegram(session, user_id)
    new_lang = schemas.UserLanguage.RU if me.language == schemas.UserLanguage.EN else schemas.UserLanguage.EN
    return await service.update(session, me, models.UserUpdate(language=new_lang))


async def update_user(user_db: models.UserDB, user_id: int, data: schemas.UserUpdate) -> schemas.User:
    resp = await service.request(f"admin/users/{user_id}", "PATCH", user_db.get_token(), json=data.model_dump())
    return schemas.User.model_validate(resp.json())


async def get_user(user_db: models.UserDB, user_id: int) -> schemas.UserWithPayrolls | None:
    resp = await service.request(f"admin/users/{user_id}", "GET", user_db.get_token())
    if resp.status_code == 200:
        user = schemas.UserWithPayrolls.model_validate(resp.json())
        return user
    return None


async def get_users(user_db: models.UserDB) -> pagination.Paginated[schemas.User]:
    resp = await service.request(
        "admin/users?page=1&per_page=100&sort=created_at&order=asc",
        "GET",
        user_db.get_token(),
    )
    return pagination.Paginated[schemas.User].model_validate(resp.json())
