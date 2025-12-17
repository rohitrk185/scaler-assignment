"""API Response Formatters matching Asana API format"""
from typing import Any, Dict, Optional, List
from fastapi.responses import JSONResponse
from fastapi import status
import json
from datetime import datetime, date


def _serialize_datetime(obj: Any) -> Any:
    """Recursively serialize datetime objects in nested structures"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, date):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: _serialize_datetime(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_serialize_datetime(item) for item in obj]
    return obj


def format_success_response(
    data: Any,
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """
    Format successful response matching Asana API format.
    
    Args:
        data: Response data (can be dict, list, or Pydantic model)
        status_code: HTTP status code
    
    Returns:
        JSONResponse with data wrapped in 'data' envelope
    """
    # Convert Pydantic models to dict with JSON serialization
    if hasattr(data, 'dict'):
        data = data.dict()
    elif hasattr(data, 'model_dump'):
        # Use mode='json' to serialize datetime and other non-JSON types
        # exclude_none=True to exclude None values
        try:
            data = data.model_dump(mode='json', exclude_none=True)
        except Exception:
            # Fallback: try without mode='json' and serialize manually
            data = data.model_dump(exclude_none=True)
            data = _serialize_datetime(data)
    
    # Ensure any remaining datetime objects are serialized
    data = _serialize_datetime(data)
    
    response_data = {"data": data}
    return JSONResponse(content=response_data, status_code=status_code)


def format_list_response(
    items: List[Any],
    status_code: int = status.HTTP_200_OK
) -> JSONResponse:
    """
    Format list response matching Asana API format.
    
    Args:
        items: List of items to return
        status_code: HTTP status code
    
    Returns:
        JSONResponse with items wrapped in 'data' array
    """
    # Convert Pydantic models to dicts with JSON serialization
    data_list = []
    for item in items:
        if hasattr(item, 'dict'):
            data_list.append(item.dict())
        elif hasattr(item, 'model_dump'):
            # Use mode='json' to serialize datetime and other non-JSON types
            data_list.append(item.model_dump(mode='json'))
        else:
            data_list.append(item)
    
    response_data = {"data": data_list}
    return JSONResponse(content=response_data, status_code=status_code)


def format_error_response(
    message: str,
    errors: Optional[List[Dict[str, Any]]] = None,
    help_text: Optional[str] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> JSONResponse:
    """
    Format error response matching Asana API format.
    
    Args:
        message: Main error message
        errors: Optional list of detailed error objects
        help_text: Optional help text
        status_code: HTTP status code
    
    Returns:
        JSONResponse with errors wrapped in 'errors' array
    """
    if errors is None:
        errors = [{"message": message}]
        if help_text:
            errors[0]["help"] = help_text
    
    response_data = {"errors": errors}
    return JSONResponse(content=response_data, status_code=status_code)

