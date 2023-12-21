from src import models, schemas
from src.services.api import service as api_service


async def get_me_response(user_db: models.UserDB, order_id: int):
    resp = await api_service.request(f"response/{order_id}/@me", "GET", user_db.get_token())
    if resp.status_code == 200:
        return schemas.OrderResponse.model_validate(resp.json())


async def get_user_response(user_db: models.UserDB, order_id: int, booster_id: str):
    resp = await api_service.request(f"response/{order_id}/{booster_id}", "GET", user_db.get_token())
    if resp.status_code == 200:
        return schemas.OrderResponse.model_validate(resp.json())


async def get_order_responses(user_db: models.UserDB, order_id: str):
    resp = await api_service.request(f"response/{order_id}/@me", "GET", user_db.get_token())
    return [schemas.OrderResponse.model_validate(r) for r in resp.json()]
