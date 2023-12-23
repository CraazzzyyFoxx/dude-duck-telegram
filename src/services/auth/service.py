import datetime

from aiogram.utils.web_app import WebAppUser
from sqlalchemy.ext.asyncio import AsyncSession

from src import models, schemas
from src.services.api import flows as api_flows
from src.services.api import service as api_service


async def register(
        session: AsyncSession, user: WebAppUser, data: schemas.SignInForm
) -> tuple[int, dict]:
    data = {
        "name": data.username,
        "email": data.email,
        "password": data.password,
    }
    response = await api_service.request_auth("auth/register", "POST", json=data)
    if response.status_code == 201:
        model = models.UserCreate(user_id=response.json()["id"], telegram_user_id=user.id)
        user_db = await api_service.create(session, model)
        status, user_db = await connect_telegram(user_db, user)
        # if status != 200:
        #     return status, response.json()
    return response.status_code, response.json()


async def login(
        session: AsyncSession, user: WebAppUser, email: str, password: str
) -> tuple[int, models.UserDB | None]:
    data = {"username": email, "password": password}
    response = await api_service.request_auth("auth/login", "POST", data=data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        user_db = await api_service.get_by_telegram(session, user.id)
        user_api = await api_flows.get_me_by_token(token)
        if user_db and user_db.user_id != user_api.id:
            return 401, None
        update_model = models.UserUpdate(user_json=user_api, token=token, last_login=datetime.datetime.utcnow())
        if not user_db:
            user_db = await api_service.create(
                session,
                models.UserCreate(user_id=user_api.id, telegram_user_id=user.id),
            )
            await api_service.update(session, user_db, update_model)
            status, user_db = await connect_telegram(user_db, user)
            # if status != 200:
            #     return status, None
        else:
            await api_service.update(session, user_db, update_model)
        return response.status_code, await api_service.get_by_telegram(session, user.id)
    return response.status_code, None


async def connect_telegram(user_db: models.UserDB, user: WebAppUser):
    if user.username is None:
        return 402, None
    status = await api_flows.connect_telegram(user_db, user)
    return status, user_db


async def request_verify(user_db: models.UserDB) -> bool:
    resp = await api_service.request("users/@me/request_verification", "POST", user_db.get_token())
    if resp.status_code == 200:
        return True
    return False


async def verify(user_db: models.UserDB, user_id: int) -> bool:
    resp = await api_service.request(f"admin/users/{user_id}/verify", "POST", user_db.get_token())
    if resp.status_code == 200:
        return True
    return False
