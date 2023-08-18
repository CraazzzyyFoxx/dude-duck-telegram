from fastapi import APIRouter, HTTPException, Depends
from starlette import status

from app.core.enums import RouteTag
from app.services.search import service as search_service

from . import models
from ..auth.bearers import requires_authorization

router = APIRouter(prefix='/render', tags=[RouteTag.ORDER_RENDERS],
                   dependencies=[Depends(requires_authorization)])


@router.get('/', response_model=list[models.RenderConfig])
async def reads_order_render_template(
        paging: search_service.models.PaginationParams = Depends(),
        sorting: search_service.models.SortingParams = Depends(),
):
    return await search_service.paginate(models.RenderConfig.find({}), paging, sorting)


@router.get('/{item_id}', response_model=models.RenderConfig)
async def read_order_render_template(item_id: int):
    model = await models.RenderConfig.get(item_id)

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A Render Template with this id does not exist."}],
        )

    return model


@router.post('/', response_model=models.RenderConfig)
async def create_order_render_template(render_config: models.RenderConfigCreate):
    model = await models.RenderConfig.get_by_name(render_config.name)

    if model:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[{"msg": "A Render Template parse with this id already exists"}],
        )

    return await render_config.create()


@router.delete('/{name}', response_model=models.RenderConfig)
async def delete_order_render_template(name: str):
    model = await models.RenderConfig.get_by_name(name)

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A Render Template with this id does not exist."}],
        )

    await model.delete_message()
    return model


@router.patch('/{name}', response_model=models.RenderConfig)
async def update_order_render_template(name: str, data: models.RenderConfigUpdate):
    model = await models.RenderConfig.get_by_name(name)

    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A Render Template with this id does not exist."}],
        )

    model.update_from(data)
    await model.save()
    return model
