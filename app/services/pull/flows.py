import typing

from . import models, service


event_map: dict[models.MessageEnum, typing.Callable] = {
    models.MessageEnum.SEND_ORDER: service.pull_create,
    models.MessageEnum.EDIT_ORDER: service.pull_update,
    models.MessageEnum.DELETE_ORDER: service.pull_delete,
    models.MessageEnum.RESPONSE_ADMINS: service.pull_admins,
    models.MessageEnum.RESPONSE_APPROVED: service.pull_booster_resp_yes,
    models.MessageEnum.RESPONSE_DECLINED: service.pull_booster_resp_no,
    models.MessageEnum.REQUEST_VERIFY: service.send_request_verify,
    models.MessageEnum.VERIFIED: service.send_verified,
    models.MessageEnum.REQUEST_CLOSE_ORDER: service.send_order_close_request,
    models.MessageEnum.LOGGED: service.send_logged_notify,
    models.MessageEnum.REGISTERED: service.send_registered_notify,
    models.MessageEnum.SENT_ORDER: service.send_order_sent_notify,
    models.MessageEnum.EDITED_ORDER: service.send_order_edited_notify,
    models.MessageEnum.DELETED_ORDER: service.send_order_deleted_notify,
    models.MessageEnum.RESPONSE_CHOSE: service.send_response_chose_notify,
    models.MessageEnum.ORDER_PAID: service.send_order_paid_notify,
}


async def process_event(event: models.MessageEvent):
    func = event_map.get(event.type)
    if func:
        return await func(**dict(event.payload))
