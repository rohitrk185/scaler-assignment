"""Error Handling Utilities"""
from fastapi import HTTPException, status
from typing import Optional, List, Dict, Any


class APIError(HTTPException):
    """Base API error exception"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        help_text: Optional[str] = None
    ):
        super().__init__(status_code=status_code, detail=message)
        self.message = message
        self.help_text = help_text


class NotFoundError(APIError):
    """Resource not found error (404)"""
    
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with id '{identifier}' not found"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            help_text=f"The requested {resource.lower()} does not exist or you don't have access to it."
        )


class ValidationError(APIError):
    """Validation error (400)"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        if field:
            message = f"Validation error for field '{field}': {message}"
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            help_text="The request body contains invalid or missing required fields."
        )


class UnauthorizedError(APIError):
    """Unauthorized access error (401)"""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            help_text="You must be authenticated to access this resource."
        )


class ForbiddenError(APIError):
    """Forbidden access error (403)"""
    
    def __init__(self, message: str = "You don't have permission to access this resource"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            help_text="You don't have the necessary permissions to perform this action."
        )


def format_error_response(
    message: str,
    errors: Optional[List[Dict[str, Any]]] = None,
    help_text: Optional[str] = None
) -> Dict[str, Any]:
    """
    Format error response to match Asana API format.
    
    Args:
        message: Main error message
        errors: Optional list of detailed error objects
        help_text: Optional help text
    
    Returns:
        Formatted error response dictionary
    """
    if errors is None:
        errors = [{"message": message}]
        if help_text:
            errors[0]["help"] = help_text
    
    return {
        "errors": errors
    }


def format_validation_errors(
    field_errors: Dict[str, List[str]]
) -> Dict[str, Any]:
    """
    Format validation errors for multiple fields.
    
    Args:
        field_errors: Dictionary mapping field names to list of error messages
    
    Returns:
        Formatted error response dictionary
    """
    errors = []
    for field, messages in field_errors.items():
        for message in messages:
            errors.append({
                "message": f"Validation error for field '{field}': {message}",
                "help": "The request body contains invalid or missing required fields."
            })
    
    return {"errors": errors}

