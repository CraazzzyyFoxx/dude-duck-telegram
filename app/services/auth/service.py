from app.services.api import flows as api_flows
from app.services.api import models as api_models
from app.services.api import service as api_service

from . import models


async def register(user_id: int, username: str, data: models.SignInForm) -> tuple[int, dict]:
    data = {"name": data.username, "email": data.email, "password": data.password,
            "telegram": username, "discord": data.discord}
    response = await api_service.request_auth('api/v1/auth/register', 'POST', json=data)
    if response.status_code == 201:
        model = api_models.TelegramUserCreate(user_id=response.json()["id"], telegram_user_id=user_id)
        await api_service.create(model)
    return response.status_code, response.json()


async def login(user_id: int, email: str, password: str) -> tuple[int, api_models.TelegramUser | None]:
    data = {'username': email, 'password': password}
    response = await api_service.request_auth('api/v1/auth/login', 'POST', data=data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        user_db = await api_service.get_by_telegram_user_id(user_id)
        user = await api_flows.get_me(token)
        if not user_db:
            await api_service.create(api_models.TelegramUserCreate(user_id=user.id, telegram_user_id=user_id))

        user_db = await api_service.get_by_telegram_user_id(user_id)
        await api_service.update(user_db, api_models.TelegramUserUpdate.model_validate({"user": user, "token": token}))
        return response.status_code, await api_service.get_by_telegram_user_id(user_id)
    return response.status_code, None


async def request_verify(user_id: int):
    user = await api_service.get_by_telegram_user_id(user_id)
    await api_service.request_auth('api/v1/auth/request-verify-token', 'POST', json={"email": user.user.email})


async def verify(token: str):
    resp = await api_service.request_auth('api/v1/auth/verify', 'POST', json={"token": token})
    if resp.status_code == 400:
        return False
    return True
