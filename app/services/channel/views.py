from fastapi import APIRouter, Depends
from beanie import PydanticObjectId

from app.core import enums
from app.services.auth.bearers import requires_authorization
from app.services.search import service as search_service

from . import models, flows, service


router = APIRouter(prefix='/channel', tags=[enums.RouteTag.ORDER_MESSAGES],
                   dependencies=[Depends(requires_authorization)])


@router.get('', response_model=search_service.models.Paginated[models.ChannelRead])
async def reads_order_channel(
        paging: search_service.models.PaginationParams = Depends(),
        sorting: search_service.models.SortingParams = Depends()
):
    return await search_service.paginate(models.Channel.find({}), paging, sorting)


@router.get('/{channel_id}', response_model=models.ChannelRead)
async def read_order_channel(channel_id: PydanticObjectId):
    return await flows.get(channel_id)


@router.post('', response_model=models.ChannelRead)
async def create_order_channel(channel: models.ChannelCreate):
    return await flows.create(channel)


@router.delete('/{channel_id}', response_model=models.ChannelRead)
async def delete_order_channel(channel_id: PydanticObjectId):
    return await flows.delete(channel_id)


@router.patch('/{channel_id}', response_model=models.ChannelRead)
async def update_order_channel(channel_id: PydanticObjectId, data: models.ChannelUpdate):
    model = await flows.get(channel_id)
    return await service.update(model, data)