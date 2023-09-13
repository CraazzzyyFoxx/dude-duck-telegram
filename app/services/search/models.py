from typing import Generic, List, TypeVar, TypedDict, Any
from enum import Enum

from pydantic import BaseModel, Field

__all__ = ("Paginated", "PaginationParams", "OrderSortingParams")


SchemaType = TypeVar("SchemaType", bound=BaseModel)


class PaginationDict(TypedDict):
    page: int
    per_page: int
    total: int
    results: List[Any]


class Paginated(BaseModel, Generic[SchemaType]):
    page: int
    per_page: int
    total: int
    results: List[SchemaType]


class PaginationParams(BaseModel):
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.per_page

    @property
    def limit(self) -> int:
        return self.per_page


class OrderSelection(Enum):
    InProgress = "In Progress"
    Completed = "Completed"
    ALL = "ALL"


class OrderSortingParams(BaseModel):
    completed: OrderSelection = OrderSelection.ALL
