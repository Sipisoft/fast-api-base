from typing import Optional, TypeVar, Generic
from fastapi.params import Query
from pydantic import Field, ConfigDict
from pydantic.generics import GenericModel
from datetime import date

def set_field_values(obj, data):
    
    update_data = data.dict(exclude_unset=True) if hasattr(data, "dict")  else data
    for key, value in update_data.items():
        setattr(obj, key, value)
    return obj

T = TypeVar("T")

class Pagination:
    def __init__(
        self,
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
        all: bool = Query(False),
        start_date: Optional[str] = Query(None, description="Start date for filtering (YYYY-MM-DD)"),
        end_date: Optional[str] = Query(None, description="End date for filtering (YYYY-MM-DD)"),
        query: Optional[str] = Query(None, description="Query string to search for")
    ):
        self.page = page if not isinstance(page, Query) else 1
        self.size = size if not isinstance(size, Query) else 20
        self.skip = (self.page - 1) * self.size
        self.limit = self.size
        self.all = all if not isinstance(all, Query) else False
        self.start_date = start_date if not isinstance(start_date, Query) else str(date.today())
        self.end_date = end_date if not isinstance(end_date, Query) else str(date.today())
        self.query = query if not isinstance(query, Query) else None

class PaginatedResponse(GenericModel, Generic[T]):
    page: int
    size: int
    data: list[T]
    total: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    @classmethod
    def from_pagination(cls, pagination: Pagination, data: list[T], total: int):
        return cls(page=pagination.page, size=pagination.size, data=data, total=total, start_date=pagination.start_date, end_date=pagination.end_date)
    

