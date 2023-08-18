from fastapi import APIRouter, Depends

from app.core import errors, enums
from app.services.auth.bearers import requires_authorization


from . import models, flows


router = APIRouter(prefix='/channel', tags=[enums.RouteTag.ORDER_MESSAGES],
                   dependencies=[Depends(requires_authorization)])


@router.get('/', response_model=list[models.OrderChannel])
async def reads_order_channel(skip: int = 0, limit: int = 100):
    return await models.OrderChannel.find({}).skip(skip).limit(limit).to_list()


@router.get('/{item_id}', response_model=models.OrderChannel)
async def read_order_channel(item_id: int):
    model = await models.OrderChannel.get(item_id)

    if not model:
        raise errors.OrderChannelNotFound(channel_id=item_id)

    return model


@router.post('/', response_model=models.OrderChannel)
async def create_order_channel(channel: models.OrderChannelCreate):
    if await models.OrderChannel.get_by_game_category(channel.game, channel.category):
        raise errors.OrderChannelAlreadyExist()

    return await models.OrderChannel(game=channel.game, channel_id=channel.channel_id,
                                     category=channel.category).create()


@router.delete('/', response_model=models.OrderChannel)
async def delete_order_channel(item_id: int):
    model = await models.OrderChannel.get(item_id)

    if not model:
        raise errors.OrderChannelNotFound(channel_id=item_id)

    return await model.delete()


@router.patch('/{item_id}', response_model=models.OrderChannel)
async def update_order_channel(item_id: int, data: models.OrderChannelUpdate):
    model = await models.OrderChannel.get(item_id)

    if not model:
        raise errors.OrderChannelNotFound(channel_id=item_id)

    model.update_from(data)
    await model.update()
    return model
