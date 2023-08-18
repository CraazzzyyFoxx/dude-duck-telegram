from fastapi import APIRouter, Depends

from app.core import errors, enums
from app.services.auth.bearers import requires_authorization


from . import models, flows


router = APIRouter(prefix='/message', tags=[enums.RouteTag.ORDER_MESSAGES],
                   dependencies=[Depends(requires_authorization)])


@router.post('')
async def send_message(data: models.MessageEvent):
    return await flows.process_event(event=data)
