"""GID validation utilities"""
import re
from typing import Optional
from fastapi import HTTPException


def is_valid_numeric_gid(gid: str) -> bool:
    """
    Check if GID is a valid numeric string (Asana format).
    Asana GIDs are numeric strings representing Long integers.
    """
    if not gid:
        return False
    # Check if it's a numeric string (all digits)
    return gid.isdigit()


def is_valid_uuid(gid: str) -> bool:
    """
    Check if GID is a valid UUID format.
    """
    if not gid:
        return False
    # UUID format: 8-4-4-4-12 hexadecimal characters
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    return bool(uuid_pattern.match(gid))


def validate_gid_format(gid: str, resource_name: str = "workspace", strict_numeric: bool = False) -> None:
    """
    Validate GID format according to OpenAPI spec.
    
    GIDs should be:
    1. Numeric strings (Asana format - Long integers) - always accepted
    2. Valid UUIDs (our internal format) - accepted unless strict_numeric=True
    
    When strict_numeric=True, only numeric strings are accepted (matches Asana exactly).
    When strict_numeric=False, both numeric strings and UUIDs are accepted.
    
    Raises HTTPException with 400 status if format is invalid.
    Matches Asana's error format: "{resource_name}: Not a Long: {gid}"
    """
    if not gid:
        raise HTTPException(
            status_code=400,
            detail={
                "errors": [
                    {
                        "message": f"{resource_name}: GID cannot be empty",
                        "help": "Please provide a valid GID"
                    }
                ]
            }
        )
    
    # Always accept numeric strings (Asana format)
    if is_valid_numeric_gid(gid):
        return
    
    # If strict_numeric, reject non-numeric GIDs
    if strict_numeric:
        raise HTTPException(
            status_code=400,
            detail={
                "errors": [
                    {
                        "message": f"{resource_name}: Not a Long: {gid}",
                        "help": "For more information on API status codes and how to handle them, read the docs on errors: https://developers.asana.com/docs/errors"
                    }
                ]
            }
        )
    
    # Accept UUIDs for backward compatibility with our internal resources
    if is_valid_uuid(gid):
        return
    
    # Reject anything else
    raise HTTPException(
        status_code=400,
        detail={
            "errors": [
                {
                    "message": f"{resource_name}: Not a Long: {gid}",
                    "help": "For more information on API status codes and how to handle them, read the docs on errors: https://developers.asana.com/docs/errors"
                }
            ]
        }
    )

