from src import schemas, models
from src.services.api import service as api_service


async def me_close_order(user_db: models.UserDB, data: schemas.CloseOrderForm):
    d = {"url": data.url, "message": data.message}
    resp = await api_service.request(
        f"users/@me/orders/close-request?order_id={data.order_id}",
        "POST",
        user_db.get_token(),
        json=d,
    )
    return resp.status_code
