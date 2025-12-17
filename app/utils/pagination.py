"""Pagination Utilities for Asana API Format"""
from typing import Optional, List, TypeVar, Generic, Dict, Any
from fastapi import Query
from app.config import settings

T = TypeVar('T')


class PaginationParams:
    """Pagination parameters matching Asana API format"""
    
    def __init__(
        self,
        limit: int = Query(
            default=settings.DEFAULT_PAGE_SIZE,
            ge=1,
            le=settings.MAX_PAGE_SIZE,
            description="Results per page. The number of objects to return per page. The value must be between 1 and 100."
        ),
        offset: Optional[str] = Query(
            default=None,
            description="Offset token. An offset to the next page returned by the API. A pagination request will return an offset token, which can be used as an input parameter to the next request. If an offset is not passed in, the API will return the first page of results."
        ),
        opt_fields: Optional[str] = Query(
            default=None,
            description="Defines fields to return. Some requests return *compact* representations of objects in order to conserve resources and complete the request more efficiently. Other times requests return more information than you may need. This parameter allows you to list the exact set of fields that the API should be sure to return for the objects. The field names should be provided as paths, described below. The id of included objects will always be returned, regardless of the field options."
        ),
        opt_pretty: Optional[bool] = Query(
            default=False,
            description="Provides “pretty” output. Provides the response in a “pretty” format. In the case of JSON this means doing proper line breaking and indentation to make it readable. This will take extra time and increase the response size so it is advisable only to use this during debugging."
        )
    ):
        self.limit = limit
        self.offset = offset
        self.opt_fields = opt_fields
        self.opt_pretty = opt_pretty


class PaginatedResponse(Generic[T]):
    """Paginated response matching Asana API format"""
    
    def __init__(
        self,
        data: List[T],
        limit: int,
        offset: Optional[str] = None,
        has_more: bool = False,
        next_offset: Optional[str] = None
    ):
        self.data = data
        self.limit = limit
        self.offset = offset
        self.has_more = has_more
        self.next_offset = next_offset
    
    def to_dict(self, base_path: str = "") -> Dict[str, Any]:
        """
        Convert to dictionary matching Asana API format.
        
        Args:
            base_path: Base path for constructing next_page URI
        
        Returns:
            Dictionary with 'data' and optional 'next_page' keys
        """
        response = {
            "data": [item.dict() if hasattr(item, 'dict') else item for item in self.data]
        }
        
        if self.has_more and self.next_offset:
            response["next_page"] = {
                "offset": self.next_offset,
                "path": base_path,
                "uri": f"{base_path}?limit={self.limit}&offset={self.next_offset}"
            }
        
        return response


def create_paginated_response(
    items: List[T],
    limit: int,
    offset: Optional[str] = None,
    base_path: str = ""
) -> PaginatedResponse[T]:
    """
    Create a paginated response from a list of items.
    
    Args:
        items: List of items to paginate
        limit: Maximum number of items per page
        offset: Current offset token (if any)
        base_path: Base path for next_page URI
    
    Returns:
        PaginatedResponse object
    """
    # Simple offset-based pagination
    # In a real implementation, you'd parse the offset token
    start_idx = 0
    if offset:
        try:
            start_idx = int(offset)
        except (ValueError, TypeError):
            start_idx = 0
    
    end_idx = start_idx + limit
    paginated_items = items[start_idx:end_idx]
    has_more = len(items) > end_idx
    next_offset = str(end_idx) if has_more else None
    
    return PaginatedResponse(
        data=paginated_items,
        limit=limit,
        offset=offset,
        has_more=has_more,
        next_offset=next_offset
    )

