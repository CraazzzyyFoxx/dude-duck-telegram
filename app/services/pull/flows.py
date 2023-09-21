import typing

from . import models, service

event_map: dict[models.MessageEnum, typing.Callable] = {
    models.MessageEnum.SEND_ORDER: service.pull_order_create,
    models.MessageEnum.EDIT_ORDER: service.pull_order_update,
    models.MessageEnum.DELETE_ORDER: service.pull_order_delete,
    models.MessageEnum.RESPONSE_ORDER_ADMINS: service.pull_order_admins,
    models.MessageEnum.RESPONSE_ORDER_APPROVED: service.pull_booster_resp_yes,
    models.MessageEnum.RESPONSE_ORDER_DECLINED: service.pull_booster_resp_no,
    models.MessageEnum.LOGGED: service.send_logged_notify,
    models.MessageEnum.REGISTERED: service.send_registered_notify,
    models.MessageEnum.REQUEST_VERIFY: service.send_request_verify,
    models.MessageEnum.VERIFIED: service.send_verified,
    models.MessageEnum.REQUEST_CLOSE_ORDER: service.send_order_close_request,
    models.MessageEnum.SENT_ORDER: service.send_order_sent_notify,
    models.MessageEnum.EDITED_ORDER: service.send_order_edited_notify,
    models.MessageEnum.DELETED_ORDER: service.send_order_deleted_notify,
    models.MessageEnum.RESPONSE_CHOSE: service.send_response_chose_notify,
    models.MessageEnum.ORDER_PAID: service.send_order_paid_notify,
    models.MessageEnum.SEND_PREORDER: service.pull_preorder_create,
    models.MessageEnum.EDIT_PREORDER: service.pull_preorder_update,
    models.MessageEnum.DELETE_PREORDER: service.pull_preorder_delete,
}


async def process_event(event: models.MessageEvent):
    func = event_map.get(event.type)
    if func:
        return await func(**dict(event.payload))
