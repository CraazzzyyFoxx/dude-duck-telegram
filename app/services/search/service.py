from typing import Type, TypeVar, Union, Any

from beanie import Document
from beanie.odm.queries.find import FindMany

from . import models

DocumentType = TypeVar("DocumentType", bound=Document)


async def paginate(
        query: FindMany,
        paging_params: models.PaginationParams,
        sorting_params: models.SortingParams,
) -> models.PaginationDict:
    results = (
        await query
        .skip(paging_params.skip)
        .limit(paging_params.limit)
        .sort((sorting_params.sort, sorting_params.order.direction))
        .to_list()
    )
    return {
        "page": paging_params.page,
        "per_page": paging_params.per_page,
        "total": await query.count(),
        "results": results,
    }
