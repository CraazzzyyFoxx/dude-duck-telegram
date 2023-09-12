from fastapi import APIRouter, Depends

from app.core import enums
from app.services.auth.bearers import requires_authorization


from . import models, flows


router = APIRouter(prefix='/message', tags=[enums.RouteTag.ORDER_MESSAGES],
                   dependencies=[Depends(requires_authorization)])


@router.post('')
async def send_message(data: dict):
    event = models.MessageEvent.model_validate(data)
    return await flows.process_event(event=event)
