from tortoise.queryset import QuerySet

from . import models


async def paginate(
        query: QuerySet,
        paging_params: models.PaginationParams,
) -> models.PaginationDict:
    results = (
        await query
        .offset(paging_params.skip)
        .limit(paging_params.limit)
        .all()
    )
    return {
        "page": paging_params.page,
        "per_page": paging_params.per_page,
        "total": await query.count(),
        "results": results,
    }
