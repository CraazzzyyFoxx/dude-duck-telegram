from app.services.api import service as api_service

from . import models


async def me_close_order(user_id: int, data: models.CloseOrderForm):
    d = {"url": data.url, "message": data.message}
    resp = await api_service.request(f'accounting/orders/{data.order_id}/close', 'POST',
                                     await api_service.get_token_user_id(user_id),
                                     json=d)
    return resp.status_code
