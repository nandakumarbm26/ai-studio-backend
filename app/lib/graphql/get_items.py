# from functools import wraps
# from fastapi import HTTPException
# from sqlalchemy import or_
# from app.db.session import get_db
# import strawberry
# from typing import Optional
# SQL_RECORDS_LIMIT = 10  # or however many per page you want

# @strawberry.input
# class ListFilters:
#     search: Optional[str] = None
#     order_by: Optional[str] = "createdDate"
#     descending: Optional[bool] = True


# def list_items(model, map_to=None, search_fields=None, default_order_by="createdDate"):
#     def decorator(resolver):
#         @wraps(resolver)
#         def wrapper(self, info, filters: Optional[ListFilters] = None, page: int = 0):
#             if page < 0:
#                 raise HTTPException(status_code=400, detail="Page must be >= 0")

#             db = next(get_db())
#             query = db.query(model)

#             # Handle search
#             if filters and filters.search and search_fields:
#                 term = f"%{filters.search.lower()}%"
#                 query = query.filter(
#                     or_(*(getattr(model, f).ilike(term) for f in search_fields))
#                 )

#             # Handle ordering
#             order_by_field = getattr(model, filters.order_by if filters and filters.order_by else default_order_by, None)
#             if not order_by_field:
#                 raise HTTPException(status_code=400, detail="Invalid order_by field")

#             if filters and filters.descending is False:
#                 query = query.order_by(order_by_field.asc())
#             else:
#                 query = query.order_by(order_by_field.desc())

#             # Pagination
#             total = query.count()
#             limit = SQL_RECORDS_LIMIT
#             offset = page * limit
#             has_more = (offset + limit) < total

#             results = query.offset(offset).limit(limit).all()
#             if map_to:
#                 results = [map_to(r) for r in results]

#             # Call resolver with internal values
#             return resolver(self, info, data=results, page=page, has_more=has_more)
#         return wrapper
#     return decorator


from functools import wraps
from typing import Callable, List, Optional, TypeVar, Any
from strawberry.types import Info
from fastapi import HTTPException
from sqlalchemy.orm import Query
from app.models.agent import PromptEngineeredAgent
import strawberry
from datetime import datetime

T = TypeVar("T")

# Define GraphQL Input Type for Query Arguments
@strawberry.input
class ListAgentsRequest:
    page: int
    s: Optional[str] = None
    order_by: Optional[str] = None



def list_items(
    model,
    map_to: Callable[[Any], Any],
    search_fields: Optional[List[str]] = None,
    default_order_by: Optional[str] = None,
    default_limit: int = 20,
    responseModel = None
):
    def decorator(resolver: Callable[..., T]) -> Callable[..., T]:
        @wraps(resolver)
        def wrapper(self, info: Info, request: ListAgentsRequest, **kwargs) -> T:
            # Page validation
            if request.page < 0:
                raise HTTPException(status_code=400, detail="Page number must be >= 0")

            db = next(info.context["get_db"]())
            query: Query = db.query(model)

            # Search logic
            if request.s and search_fields:
                from sqlalchemy import or_
                conditions = [getattr(model, field).ilike(f"%{request.s}%") for field in search_fields]
                query = query.filter(or_(*conditions))

            # Order logic
            order_attr = getattr(model, request.order_by or default_order_by, None)
            if order_attr is None:
                raise HTTPException(status_code=400, detail="Invalid order_by field")
            query = query.order_by(order_attr.desc())

            # Pagination logic
            offset = request.page * default_limit
            items = query.offset(offset).limit(default_limit + 1).all()
            has_more = len(items) > default_limit
            items = items[:default_limit]

            # Mapping items
            mapped_items = [map_to(item) for item in items]
            data = responseModel(data=mapped_items, page=request.page, has_more=has_more)
            return resolver(self, info, request, data, **kwargs)
        return wrapper
    return decorator
