"""Users API Endpoints"""
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.utils.pagination import PaginationParams, create_paginated_response
from app.utils.responses import format_success_response, format_list_response, format_error_response
from app.utils.errors import NotFoundError
from app.utils.request_parsing import parse_request_body
from app.config import settings

router = APIRouter()


@router.get("/users", response_model=dict)
async def get_users(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get all users.
    
    Returns a list of all users accessible to the authenticated user.
    """
    try:
        users = db.query(User).all()
        
        paginated = create_paginated_response(
            items=users,
            limit=pagination.limit,
            offset=pagination.offset,
            base_path=f"{settings.API_V1_PREFIX}/users"
        )
        
        response_data = {
            "data": [
                UserResponse(
                    gid=u.gid,
                    resource_type=u.resource_type or "user",
                    name=u.name,
                    email=u.email,
                    photo=u.photo,
                    workspaces=None,
                    custom_fields=None
                ).model_dump(exclude_none=True)
                for u in paginated.data
            ]
        }
        
        if paginated.has_more and paginated.next_offset:
            response_data["next_page"] = {
                "offset": paginated.next_offset,
                "path": f"{settings.API_V1_PREFIX}/users",
                "uri": f"{settings.API_V1_PREFIX}/users?limit={pagination.limit}&offset={paginated.next_offset}"
            }
        
        return response_data
    
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.get("/users/{user_gid}", response_model=dict)
async def get_user(
    user_gid: str,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a specific user.
    
    Returns the full record for a single user.
    """
    try:
        user = db.query(User).filter(User.gid == user_gid).first()
        
        if not user:
            raise NotFoundError("User", user_gid)
        
        user_response = UserResponse(
            gid=user.gid,
            resource_type=user.resource_type or "user",
            name=user.name,
            email=user.email,
            photo=user.photo,
            workspaces=None,
            custom_fields=None
        )
        
        return format_success_response(user_response)
    
    except NotFoundError as e:
        return format_error_response(
            message=str(e.message),
            help_text=str(e.help_text),
            status_code=e.status_code
        )
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.put("/users/{user_gid}", response_model=dict)
async def update_user(
    user_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Update a user.
    
    Updates the fields of a user. Only the fields provided in the request will be updated.
    Request body must follow OpenAPI spec format: {"data": {"name": "..."}}
    """
    try:
        user = db.query(User).filter(User.gid == user_gid).first()
        
        if not user:
            raise NotFoundError("User", user_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        user_data = parse_request_body(request_body, UserUpdate)
        
        update_dict = user_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        user_response = UserResponse(
            gid=user.gid,
            resource_type=user.resource_type or "user",
            name=user.name,
            email=user.email,
            photo=user.photo,
            workspaces=None,
            custom_fields=None
        )
        
        return format_success_response(user_response)
    
    except NotFoundError as e:
        return format_error_response(
            message=str(e.message),
            help_text=str(e.help_text),
            status_code=e.status_code
        )
    except Exception as e:
        db.rollback()
        return format_error_response(
            message=str(e),
            status_code=500
        )

