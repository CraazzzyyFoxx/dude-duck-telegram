from app.services.api import service as api_service

from . import models


async def get_me_response(user_id: int, order_id: str):
    resp = await api_service.request(f'response/{order_id}/@me', 'GET', await api_service.get_token_user_id(user_id))
    if resp.status_code == 200:
        return models.OrderResponse.model_validate(resp.json())


async def get_user_response(user_id: int, order_id: str, booster_id: str):
    resp = await api_service.request(f'response/{order_id}/{booster_id}', 'GET',
                                     await api_service.get_token_user_id(user_id))
    if resp.status_code == 200:
        return models.OrderResponse.model_validate(resp.json())


async def get_order_responses(user_id: int, order_id: str):
    resp = await api_service.request(f'response/{order_id}/@me', 'GET',
                                     await api_service.get_token_user_id(user_id))
    return [models.OrderResponse.model_validate(r) for r in resp.json()]
