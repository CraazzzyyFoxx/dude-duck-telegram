from fastapi import APIRouter, Depends

from app.core import enums
from app.services.auth.bearers import requires_authorization
from app.services.search import service as search_service

from . import flows, models

router = APIRouter(prefix='/render', tags=[enums.RouteTag.ORDER_RENDERS],
                   dependencies=[Depends(requires_authorization)])


@router.get('', response_model=search_service.models.Paginated[models.RenderConfigRead])
async def reads_render_config(
        paging: search_service.models.PaginationParams = Depends(),
):
    return await search_service.paginate(models.RenderConfig.filter(), paging)


@router.get('/{name}', response_model=models.RenderConfigRead)
async def read_render_config(name: str):
    return await flows.get_by_name(name)


@router.post('', response_model=models.RenderConfigRead)
async def create_render_config(model: models.RenderConfigCreate,):
    return await flows.create(model)


@router.delete('/{name}')
async def delete_render_config(name: str):
    return await flows.delete(name)


@router.patch('/{name}', response_model=models.RenderConfigRead)
async def update_render_config(name: str, data: models.RenderConfigUpdate):
    return await flows.update(name, data)
