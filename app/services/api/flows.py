from beanie import PydanticObjectId

from app.services.search import service as search_service

from . import models, service, schemas


async def get_me(token: str) -> models.User | None:
    resp = await service.request('users/@me', 'GET', token)
    if resp.status_code == 200:
        return models.User.model_validate(resp.json())


async def get_me_user_id(user_id: int) -> models.User | None:
    resp = await service.request('users/@me', 'GET', await service.get_token_user_id(user_id))
    if resp.status_code == 200:
        user = models.User.model_validate(resp.json())
        user_db = await service.get_by_telegram_user_id(user_id)
        await service.update(user_db, models.TelegramUserUpdate(user=user))
        return models.User.model_validate(resp.json())


async def me_get_orders(
        user_id: int,
        status: models.OrderSelection,
        page: int = 1
) -> search_service.models.Paginated[schemas.OrderRead]:
    resp = await service.request(
        f'users/@me/orders?page={page}&per_page=10&sort=created_at&order=asc&completed={status.value}',
        'GET',
        await service.get_token_user_id(user_id)
    )
    return search_service.models.Paginated[schemas.OrderRead].model_validate(resp.json())


async def get_me_accounting(user_id: int) -> dict:
    resp = await service.request('accounting/@me', 'GET', await service.get_token_user_id(user_id))
    if resp.status_code == 200:
        return resp.json()


async def get_order(user_id: int, order_id: PydanticObjectId) -> schemas.Order:
    resp = await service.request(f'users/@me/orders/{str(order_id)}/telegram', 'GET',
                                 await service.get_token_user_id(user_id))
    return schemas.Order.model_validate(resp.json())
