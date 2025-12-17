"""Utilities for parsing OpenAPI-compliant request bodies"""
from typing import TypeVar, Type
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


def parse_request_body(request_body: dict, schema_class: Type[T]) -> T:
    """
    Parse request body that follows Asana API format: {"data": {...}}
    
    Args:
        request_body: The request body dict (may have "data" wrapper or not)
        schema_class: The Pydantic schema class to parse into
    
    Returns:
        Parsed schema instance
    """
    # If request body has "data" key, extract it
    if "data" in request_body:
        data = request_body["data"]
    else:
        # If no "data" wrapper, use the whole body
        data = request_body
    
    # Parse using the schema class
    return schema_class(**data)

