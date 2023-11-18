from app.services.api import service as api_service

from . import models


async def me_close_order(user_id: int, data: models.CloseOrderForm):
    d = {"url": data.url, "message": data.message}
    resp = await api_service.request(
        f"users/@me/orders/close-request?order_id={data.order_id}",
        "POST",
        await api_service.get_token_user_id(user_id),
        json=d
    )
    return resp.status_code
